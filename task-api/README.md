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

## Swagger UI

Interactive docs are available at http://localhost:8000/docs.

![Swagger UI](screenshots/swagger.png)
