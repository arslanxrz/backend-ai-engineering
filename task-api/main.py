from fastapi import FastAPI , HTTPException , Body

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

@app.post("/tasks" , status_code=201)
def create_task(title:str = Body(..., embed=True)):
    if not title or title.strip():
        raise HTTPException(
            status_code=400,
            detail={"error":"what's wrong"}
        )
    id = tasks[-1]['id']+1 if tasks else 1
    task = {"id":id , "title":title , "done":False}
    tasks.append(task)
    return task
    
