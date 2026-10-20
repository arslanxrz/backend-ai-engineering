from fastapi import FastAPI , HTTPException , Body , Response , Depends
from pydantic import BaseModel, field_validator
import sqlite3

app = FastAPI(title="Task API" , version="1.0")

DATABASE_NAME = "tasks.db"

tasks = [
    {"id" : 1 , "title":"Buy milk" , "done":False},
    {"id" : 2 , "title":"Water the plants" , "done":True},
    {"id" : 3 , "title":"Backup files" , "done":False}
]

class task_val(BaseModel):
    title : str | None = None
    done : bool | None = None

def get_db():
    """Connect to sqlite database"""
    conn = sqlite3.connect(DATABASE_NAME , check_same_thread=False)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,
        title TEXT,
        done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
        )
        """)

        cursor.execute("select COUNT(*) from tasks")
        row_count = cursor.fetchone()[0]
        if row_count==0:
            example_tasks = [
                (1 , "Buy milk" , 0),
                (2 , "Water the plants" , 1),
                (3 , "Backup files" , 0)
            ]
            cursor.executemany("INSERT INTO tasks(id , title , done) VALUES (?,?,?)",example_tasks)
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
        detail={ "error": "Task 99 not found" }
    )

@app.post("/tasks" , status_code=201 , summary="create a task" , description="Creates a tasks from the JSON body with a title")
def create_task(title:str = Body(..., embed=True)):
    if not title or title.strip()=="":
        raise HTTPException(
            status_code=400,
            detail={"error":"what's wrong"}
        )
    id = tasks[-1]['id']+1 if tasks else 1
    task = {"id":id , "title":title , "done":False}
    tasks.append(task)
    return task

@app.put("/tasks/{id}" , summary="Update a task" , description="Changes the title and/or the done status of the task")
def update_task(id:int , update_data : task_val):
    unknown_id = id not in [task["id"] for task in tasks]
    if unknown_id:
        raise HTTPException(
            status_code=404,
            detail="Unknown ID"
        )
    task = tasks[id-1]
    updated_data = update_data.model_dump(exclude_none=True)
    if not updated_data:
        raise HTTPException(status_code=400, detail="Empty request body. Provide at least one field to update.")
    task.update(updated_data)
    return task

@app.delete("/tasks/{id}" , status_code=204, summary="Delete a task" , description="Removes the task with the given ID")
def delete_task(id:int):
    for task in tasks:
        if task['id']==id:
            tasks.remove(task)
            return 
    raise HTTPException(
        status_code=404,
        detail="Unkown ID"
    )

# Extras
@app.get("/filter_tasks" , summary="Filter Task")
def get_filtered_tasks(done:bool):
    print(done)
    filtered_tasks = [task for task in tasks if task["done"]==done]
    return filtered_tasks

@app.get("/stats" , summary="Get statistics")
def get_stats():
    done_count = len([task for task in tasks if task['done']==True])
    return { "total": len(tasks), "done": done_count, "open": len(tasks) - done_count }
    
