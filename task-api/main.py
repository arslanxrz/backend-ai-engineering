from pickle import FALSE, TRUE
from fastapi import FastAPI , HTTPException , Body , Response , Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import sqlite3
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os

app = FastAPI(title="Task API" , version="1.0")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           
    allow_credentials=True,         
    allow_methods=["*"],             
    allow_headers=["*"],             
)

class task_val(BaseModel):
    title : str | None = None
    done : bool | None = None 

def get_db():
    """Connect to sqlite database"""
    conn = psycopg.connect(DATABASE_URL , row_factory=dict_row)

    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,
        title TEXT,
        done BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)

        cursor.execute("select COUNT(*) from tasks")
        row_count = cursor.fetchone()[0]
        if row_count==0:
            example_tasks = [
                (1 , "Buy milk" , False),
                (2 , "Water the plants" , True),
                (3 , "Backup files" , False)
            ]
            cursor.executemany("INSERT INTO tasks(id , title , done) VALUES (%s,%s,%s)",example_tasks)
            conn.commit()
            print("Database seeded with 3 example")
        else:
            print("Table already has data. Skiping seeding.")


init_db()


@app.get("/" , summary="API info" , description="Returns the name, version and main endpoints of this API.")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health" , summary="Health check" , description="Returns status ok if the server is alive.")
async def health():
    return {"status":"ok"}

@app.get("/tasks" , summary="List all tasks" , description="Returns every task in the in-memory list.")
def get_tasks(db:sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * from tasks")

    rows = cursor.fetchall()
    return rows


@app.get("/tasks/{id}" , summary="Get one task" , description="Return one task with the given id")
def get_task_by_id(id:int , db:sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * from tasks where id = ?" , (id,))

    row = cursor.fetchone()
    if row:
        return row
    raise HTTPException(
        status_code=404,
        detail={ "error": f"Task {id} not found" }
    )

@app.post("/tasks" , status_code=201 , summary="create a task" , description="Creates a tasks with a title")
def create_task(title:str = Body(default=None, embed=True) , db:sqlite3.Connection=Depends(get_db)):
    cursor = db.cursor()
    if not title or title.strip()=="":
        raise HTTPException(
            status_code=400,
            detail={"error":"what's wrong"}
        )
    
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)",(title , 0))
    db.commit()
    row_id = cursor.lastrowid
    return {"id":row_id , "title":title , "done":0}


@app.put("/tasks/{id}" , summary="Update a task" , description="Changes the title and/or the done status of the task")
def update_task(id:int , update_data : task_val , db:sqlite3.Connection = Depends(get_db)):

    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks where id = ?", (id,))
    task = cursor.fetchone()
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown ID"
        )

    data = update_data.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Empty request body. Provide at least one field to update.")
    
    fields = ", ".join(f"{key} = ?" for key in data)
    values = list(data.values())
    values.append(id)
    cursor.execute(f"UPDATE tasks SET {fields} WHERE id = ?", values)

    db.commit()

    cursor.execute("SELECT * FROM tasks where id = ?", (id,))
    task = cursor.fetchone()
    return task

@app.delete("/tasks/{id}" , status_code=204, summary="Delete a task" , description="Removes the task with the given ID")
def delete_task(id:int , db:sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks where id = ?", (id,))
    task = cursor.fetchone()
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown ID"
        )
    cursor.execute("DELETE FROM tasks WHERE id = ?" , (id,))
    db.commit()
    return 

# Extras

@app.get("/search_tasks",summary="Search tasks using keyword")
def search_tasks(search:str , db:sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE title LIKE ?" , (f"%{search}%",))
    searched_task = cursor.fetchall()
    if not searched_task:
        raise HTTPException(status_code=404 , detail="No tasks found matching the keyword")
    return searched_task

@app.get("/filter_tasks" , summary="Filter Task")
def get_filtered_tasks(done:int , db:sqlite3.Connection=Depends(get_db)):

    cursor = db.cursor()
    cursor.execute("SELECT * from tasks where done = ?" , (done,))
    filtered_task = cursor.fetchall()
    if not filtered_task:
        raise HTTPException(status_code=404 , detail="No tasks exist")
    return filtered_task

@app.get("/sort_tasks")
def get_sorted_tasks(db:sqlite3.Connection=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY title")
    sorted_task = cursor.fetchall()
    if not sorted_task:
        raise HTTPException(status_code=404 , detail="No tasks exist")
    return sorted_task


@app.get("/stats" , summary="Get statistics")
def get_stats(db:sqlite3.Connection=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) from tasks")
    count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) from tasks where done = 1")
    done_count = cursor.fetchone()[0]
    return { "total": count, "done": done_count, "open": count - done_count }
    
