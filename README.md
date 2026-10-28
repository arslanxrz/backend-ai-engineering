# FlyRank Internship, Backend AI Engineering Track

Assignments for the FlyRank Internship, Backend Track. Language: **Python**.

## Assignments

| ID  | Task                                        | Folder                 | Status      |
| --- | ------------------------------------------- | ---------------------- | ----------- |
| A1  | Build a CRUD API (FastAPI, in-memory)       | [task-api](./task-api) | Done        |
| A2  | Move storage to SQLite                      | [task-api](./task-api) | Done        |
| A3  | Containerize the stack (Postgres + Docker)  | [task-api](./task-api) | Done |

All of these assignments are one project that grows each week, so they share the
`task-api` folder. Each assignment's final state is tagged in Git
(`a1-submission`, `a2-submission`, ...).

## Quick start (Docker)

**Requirement:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

```bash
git clone https://github.com/arslanxrz/backend-ai-engineering.git
cd backend-ai-engineering/task-api
cp .env.example .env
docker compose up --build
```

On Windows Command Prompt, use `copy .env.example .env` instead of `cp`.

Then open:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

The first run seeds three example tasks. To stop everything, press `Ctrl+C`, then run:

```bash
docker compose down
```

Your data is kept in a Docker volume and survives `down` and `up`. Use `docker compose down -v` to wipe it too.

## More details

See [`task-api/README.md`](./task-api/README.md) for environment variables,
the endpoint table, database details, and screenshots.

## Author

ARSLAN RAZA, [https://github.com/arslanxrz](https://github.com/arslanxrz)