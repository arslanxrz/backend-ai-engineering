from fastapi import FastAPI , HTTPException

app = FastAPI()

tasks = [
    {"id" : 1 , "tittle":"Buy milk" , "done":False},
    {"id" : 2 , "tittle":"Water the plants" , "done":True},
    {"id" : 3 , "tittle":"Backup files" , "done":False}
]


@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{id}")
def get_task_by_id(id:int):
    for task in tasks:
        if(task["id"]==id):
            return task
    raise HTTPException(
        status_code=404,
        detail={ "error": "Task 99 not found" }
    )
    
