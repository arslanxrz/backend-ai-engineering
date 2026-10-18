
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

# In-memory storage: no database required
tasks = [
    {"id": 1, "title": "Learn Python", "done": True},
    {"id": 2, "title": "Build a FastAPI project", "done": False},
    {"id": 3, "title": "Write API tests", "done": False},
]

app = FastAPI(title="Task API", version="1.0")


# Return 400 instead of FastAPI's default 422 for invalid requests
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid or missing request data"},
    )


# Request body validation
class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    done: bool


# Helper function
def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")


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
    return tasks


# 4. Get one task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return find_task(task_id)


# 5. Create a task
@app.post("/tasks", status_code=201)
def create_task(task_data: TaskCreate):
    new_id = max((task["id"] for task in tasks), default=0) + 1

    new_task = {
        "id": new_id,
        **task_data.model_dump(),
    }

    tasks.append(new_task)
    return new_task


# 6. Update an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    task = find_task(task_id)

    task["title"] = task_data.title
    task["done"] = task_data.done

    return task


# 7. Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)

    return {
        "message": "Task deleted successfully",
        "task": task,
    }


# 8. Filter tasks by completion status
@app.get("/filter_task")
def filter_tasks(done: bool):
    return [task for task in tasks if task["done"] == done]


# 9. Get task statistics
@app.get("/stats")
def get_stats():
    total = len(tasks)
    completed = sum(1 for task in tasks if task["done"])
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
    }
