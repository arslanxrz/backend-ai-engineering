
import sqlite3
from contextlib import closing

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field


DATABASE = "tasks.db"

app = FastAPI(title="Task API", version="1.0")


# Database connection helper
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create the table if it does not exist.
# Seed the initial tasks only when the table is empty.
def initialize_database():
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT 0
                        CHECK (done IN (0, 1))
                )
            """)

            count = conn.execute(
                "SELECT COUNT(*) FROM tasks"
            ).fetchone()[0]

            if count == 0:
                conn.executemany(
                    "INSERT INTO tasks (title, done) VALUES (?, ?)",
                    [
                        ("Learn Python", 1),
                        ("Build a FastAPI project", 0),
                        ("Write API tests", 0),
                    ],
                )


@app.on_event("startup")
def startup():
    initialize_database()


# Return 400 instead of FastAPI's default 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid or missing request data"},
    )


# Request validation models
class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


# Helper to retrieve a task or return 404
def find_task(task_id: int):
    with closing(get_connection()) as conn:
        task = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task["id"],
        "title": task["title"],
        "done": bool(task["done"]),
    }


# 1. API information
@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


# 2. Health check
@app.get("/health")
def health():
    return {"status": "ok"}


# 3. Get all tasks
@app.get("/tasks")
def get_tasks():
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
        }
        for row in rows
    ]


# 4. Get one task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return find_task(task_id)


# 5. Create a task
@app.post("/tasks", status_code=201)
def create_task(task_data: TaskCreate):
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (task_data.title, int(task_data.done)),
            )
            new_id = cursor.lastrowid

        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (new_id,),
        ).fetchone()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


# 6. Update an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    updates = task_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                "SELECT id FROM tasks WHERE id = ?",
                (task_id,),
            )
            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found",
                )

            set_clause = ", ".join(
                f"{field} = ?" for field in updates
            )
            values = [
                int(value) if field == "done" else value
                for field, value in updates.items()
            ]
            values.append(task_id)

            conn.execute(
                f"UPDATE tasks SET {set_clause} WHERE id = ?",
                values,
            )

        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


# 7. Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with closing(get_connection()) as conn:
        with conn:
            row = conn.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found",
                )

            task = {
                "id": row["id"],
                "title": row["title"],
                "done": bool(row["done"]),
            }

            conn.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )

    return {
        "message": "Task deleted successfully",
        "task": task,
    }


# 8. Filter tasks by completion status
@app.get("/filter_task")
def filter_tasks(done: bool):
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE done = ?
            ORDER BY id
            """,
            (int(done),),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
        }
        for row in rows
    ]


# 9. Get task statistics
@app.get("/stats")
def get_stats():
    with closing(get_connection()) as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(done), 0) AS completed
            FROM tasks
        """).fetchone()

    total = row["total"]
    completed = row["completed"]

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
    }
