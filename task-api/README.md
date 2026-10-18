# Task API

A to-do list API built with FastAPI. Supports full CRUD on tasks.

## Tech stack

- Python 3.10+, FastAPI, Uvicorn

## Setup and run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Table of all the endpoints

| Endpoint | summary | description |

| --- | --- | --- |
| / | API info | Returns the name, version and main endpoints of this API. |
| /health | Health check | Returns status ok if the server is alive. |
| /tasks | List all tasks | Returns every task in the in-memory list. |
| /tasks/{id} | Get one task | Return one task with the given id |
| /tasks | create a task | Creates a tasks from the JSON body with a title |
| /tasks/{id} | Update a task | Changes the title and/or the done status of the task |
| /tasks/{id} | Delete a task | Removes the task with the given ID |

## curl -i output

### Command

curl -i http://localhost:8000/

### output

HTTP/1.1 200 OK
date: Sun, 18 Oct 2026 03:46:52 GMT
server: uvicorn
content-length: 58
content-type: application/json

{"name":"Task API","version":"1.0","endpoints":["/tasks"]}

## Swagger UI

Interactive docs are available at http://localhost:8000/docs.

![Swagger UI](screenshots/swagger.png)
