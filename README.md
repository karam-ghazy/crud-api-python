# Task API

A CRUD REST API for managing tasks, built with Python and FastAPI as a backend engineering learning project. The project started with in-memory storage, moved to SQLite, and now runs on **PostgreSQL inside Docker**, orchestrated with **Docker Compose** so the entire stack starts with a single command.

## Description

This project implements a complete CRUD (Create, Read, Update, Delete) REST API for managing a task list.

The API endpoints, request formats, validation rules, and HTTP status codes have stayed identical across every storage backend the project has used. Only the storage layer has changed each time — first from an in-memory Python list to SQLite, and now from SQLite to PostgreSQL. That stability is intentional: the project is structured so the API layer and the data layer are cleanly separated, and swapping one doesn't require touching the other.

The current architecture is:

```text
Client
   ↓
FastAPI Container
   ↓
PostgreSQL Container
   ↓
Docker Volume
```

Both containers are started together with:

```bash
docker compose up
```

## Technologies Used

* Python 3.10+
* FastAPI
* Uvicorn
* Pydantic
* PostgreSQL
* `psycopg2`
* `python-dotenv`
* Docker & Docker Compose
* Swagger UI
* Git & GitHub

## Project Structure

```text
task-api/
│
├── main.py
├── repositories/
│   └── postgres_task_repository.py
├── sql/
│   └── init.sql
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── Requirements.txt
├── README.md

```

## Storage Implementation

This project now uses **PostgreSQL**, running in Docker, as its storage layer — replacing the earlier SQLite implementation.

The swap was done by writing a PostgreSQL repository (`repositories/postgres_task_repository.py`) that exposes the same functions and return shapes the SQLite code provided: `get_all_tasks()`, `get_task(id)`, `create_task(title)`, `update_task(id, title, done)`, and `delete_task(id)`. The FastAPI routes in `main.py` were updated only to call this repository instead of running `sqlite3` queries directly — no route paths, request/response formats, validation rules, or HTTP status codes changed in the process. This demonstrates that the storage implementation is fully decoupled from the API layer.

## Database

The database is PostgreSQL, running in a Docker container, with schema defined in `sql/init.sql`:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
```

| Column  | Type    | Description                            |
| ------- | ------- | -------------------------------------- |
| `id`    | SERIAL  | Unique task identifier and primary key |
| `title` | TEXT    | Task title                             |
| `done`  | BOOLEAN | Whether the task is completed          |

This schema is applied automatically the first time the PostgreSQL container starts against an empty data volume — the official Postgres image runs every `.sql` file it finds bind-mounted into `/docker-entrypoint-initdb.d/`, which is where `docker-compose.yml` mounts `sql/init.sql`. On every later restart, this step is skipped automatically once the volume already contains data.

## Running with Docker Compose (current method)

This is the primary way to run the project — one command starts both the API and the database.

**1. Set up your environment file**

```bash
cp .env.example .env
```

Then edit `.env` with real values if needed. The defaults used throughout this project are:

```env
DATABASE_URL=postgresql://taskuser:taskpassword@localhost:5432/tasks
POSTGRES_DB=tasks
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpassword
```

`.env` is gitignored and never committed; `.env.example` documents the required shape with placeholder values only.

**2. Start the stack**

```bash
docker compose up
```

The first run builds the FastAPI image and pulls the official `postgres:16` image, which can take a minute. Add `--build` to force a rebuild after changing code or dependencies:

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up -d
```

**3. The API is available at**

```text
http://localhost:8000
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

**4. Stop the stack**

```bash
docker compose down
```

This stops and removes the containers, but **keeps the named Docker volume** — task data is not lost. See [Persistence Test](#persistence-test) below.

## Running Locally Without Docker (legacy method)

The application can still run directly with `uvicorn`, provided a PostgreSQL instance is reachable at the connection string in `.env` (for example, a Postgres container started manually rather than through Compose).

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install -r Requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Environment Variables

Configuration is read from `.env` via `python-dotenv` — no credentials are hard-coded in the Python source.

| Variable            | Purpose                                                                                |
| ------------------- | --------------------------------------------------------------------------------------- |
| `DATABASE_URL`      | Full connection string, used when running the app directly on the host (`localhost`)    |
| `POSTGRES_DB`       | Database name, used by Docker Compose to configure the `db` service                     |
| `POSTGRES_USER`     | Database user, used by Docker Compose                                                   |
| `POSTGRES_PASSWORD` | Database password, used by Docker Compose                                               |

Inside Docker Compose, the FastAPI container does **not** connect to PostgreSQL using `localhost`. Each container has its own isolated network namespace, so `localhost` inside the app container refers to the app container itself — not the database. Docker Compose gives every service a hostname matching its service name, resolved automatically over the Compose network. Since the PostgreSQL service is named `db`, `docker-compose.yml` builds the app's connection string as:

```text
postgresql://taskuser:taskpassword@db:5432/tasks
```

using `db:5432` instead of `localhost:5432`. This override is set directly in `docker-compose.yml`'s `environment:` block for the `app` service, so it takes precedence over the `localhost`-based value in the committed `.env` file whenever the app runs inside Compose.

## API Endpoints

| Method | Endpoint      | Description                                         |
| ------ | ------------- | --------------------------------------------------- |
| GET    | `/`           | Returns API name, version, and endpoint information |
| GET    | `/health`     | Returns server health status                        |
| GET    | `/tasks`      | Returns all tasks from PostgreSQL                    |
| GET    | `/tasks/{id}` | Returns a single task by ID                          |
| POST   | `/tasks`      | Creates a new task in PostgreSQL                     |
| PUT    | `/tasks/{id}` | Updates an existing task                             |
| DELETE | `/tasks/{id}` | Deletes a task                                       |

The API endpoints, request/response shapes, and status codes are unchanged from the SQLite implementation — only the storage layer has changed.

## Example Usage

### Get All Tasks

```bash
curl -i http://localhost:8000/tasks
```

Example response:

```text
HTTP/1.1 200 OK
content-type: application/json
```

```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "done": false
  },
  {
    "id": 2,
    "title": "Build CRUD API",
    "done": false
  }
]
```

### Get a Single Task

```bash
curl -i http://localhost:8000/tasks/1
```

```text
HTTP/1.1 200 OK
```

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "done": false
}
```

### Create a Task

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

```text
HTTP/1.1 201 Created
```

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

The new task is inserted into PostgreSQL.

### Update a Task

```bash
curl -i -X PUT http://localhost:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

```text
HTTP/1.1 200 OK
```

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": true
}
```

### Delete a Task

```bash
curl -i -X DELETE http://localhost:8000/tasks/4
```

```text
HTTP/1.1 204 No Content
```

The task is removed from PostgreSQL.

## Validation Rules

The API validates incoming data before touching the database.

### POST `/tasks`

The `title` field is required and cannot be empty or contain only whitespace.

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```

```text
400 Bad Request
```

### PUT `/tasks/{id}`

At least one of `title` or `done` must be provided in the request body. An empty body returns `400 Bad Request`. If `title` is provided, it cannot be empty or whitespace-only.

## HTTP Status Codes

| Status | Meaning                                                               |
| ------ | ---------------------------------------------------------------------- |
| 200    | Successful GET or PUT request                                          |
| 201    | Task successfully created                                              |
| 204    | Task successfully deleted                                              |
| 400    | Invalid request body                                                   |
| 404    | Task ID not found                                                      |
| 422    | Request body is missing a required field or fails Pydantic validation  |

## Error Handling

If a requested task does not exist, the API returns `404`:

```bash
curl -i http://localhost:8000/tasks/99
```

```json
{
  "detail": "Task 99 not found"
}
```

## Working Directly With PostgreSQL

The database can also be inspected and modified directly, bypassing the API, to confirm both are working against the same persistent data.

Open a `psql` shell inside the running container:

```bash
docker exec -it $(docker compose ps -q db) psql -U taskuser -d tasks
```

### List all tables

```sql
\dt
```

### Describe the tasks table

```sql
\d tasks
```

### List all tasks

```sql
SELECT * FROM tasks ORDER BY id;
```

### Show completed tasks

```sql
SELECT * FROM tasks WHERE done = true;
```

### Count all tasks

```sql
SELECT COUNT(*) FROM tasks;
```

### Mark all tasks as completed

```sql
UPDATE tasks SET done = true;
```

### Delete completed tasks

```sql
DELETE FROM tasks WHERE done = true;
```

Changes made directly in `psql` are immediately visible through the API:

```bash
curl -i http://localhost:8000/tasks
```

This confirms the API and the database are reading and writing the same underlying data — not two separate copies.

## Persistence Test

To confirm that PostgreSQL data survives a full stack restart — not just an application restart — the following test was performed:

1. The stack was started with `docker compose up -d`.
2. A task titled **"Persistence Test"** was created via `POST /tasks`.
3. `GET /tasks` confirmed the task was present, with its assigned `id`.
4. The stack was stopped with `docker compose down` — this removes the containers, but not the named Docker volume.
5. The stack was started again with `docker compose up -d`.
6. `GET /tasks` was called again — the **"Persistence Test"** task was still present, with the same `id` and title.

This confirms that PostgreSQL's data directory, backed by the named Docker volume `pgdata`, is what preserves task data independently of the container lifecycle. `docker compose down` removes containers but not volumes; only an explicit `docker compose down -v` (or `docker volume rm`) would delete this data.

The volume itself can be inspected directly:

```bash
docker volume ls
docker volume inspect crud-api-python_pgdata
```

## Interactive Documentation — Swagger UI

FastAPI automatically generates interactive API documentation. With the stack running, open:

```text
http://localhost:8000/docs
```

Swagger UI provides access to all endpoints and allows requests to be sent directly from the browser using **Try it out**.

## CRUD Flow

```text
CREATE
POST /tasks
      ↓
Repository INSERT
      ↓
PostgreSQL
      ↓
READ
GET /tasks
      ↓
UPDATE
PUT /tasks/{id}
      ↓
Repository UPDATE
      ↓
PostgreSQL
      ↓
DELETE
DELETE /tasks/{id}
      ↓
Repository DELETE
      ↓
PostgreSQL
```

## Project Progression

### Week 2 — In-Memory Storage

```text
FastAPI → Python List
```

Restarting the server erased all data.

### Week 3 — SQLite

```text
FastAPI → sqlite3 → tasks.db
```

Data persisted across server restarts, stored in a single local file.

### Week 4 — PostgreSQL in Docker + Docker Compose

```text
FastAPI Container → PostgreSQL Container → Docker Volume
```

The database moved out of a local file and into a real, separately running database server, containerized with Docker. This stage was broken into discrete steps:

1. **Run PostgreSQL in Docker** with a named volume for persistence.
2. **Move configuration into `.env`**, gitignored, with a committed `.env.example`.
3. **Define the schema in `sql/init.sql`**, applied automatically on first container startup.
4. **Write a PostgreSQL repository** implementing the same interface the SQLite code exposed, then swap it into `main.py` — the routes and validation logic did not change.
5. **Write a `Dockerfile` and `docker-compose.yml`** so the FastAPI app and PostgreSQL start together with one command.
6. **Prove persistence** across a full `docker compose down` / `docker compose up` cycle.

Across all of this, the API's endpoints, request/response formats, and status codes never changed — only the storage layer did.

> The API defines what the application does, while the data layer defines where the application stores its data.

## Learning Outcomes

Through this project, I practiced:

* Building REST API endpoints with FastAPI
* Implementing CRUD operations
* Using HTTP methods correctly
* Handling HTTP status codes
* Validating request data with Pydantic
* Separating API logic from storage logic via a repository pattern
* Connecting FastAPI to SQLite, and later to PostgreSQL
* Writing PostgreSQL schema with `CREATE TABLE IF NOT EXISTS`
* Using parameterized SQL queries to prevent SQL injection
* Running PostgreSQL in Docker with a persistent named volume
* Managing configuration and secrets with `.env` / `.env.example`
* Writing a `Dockerfile` to containerize a FastAPI application
* Orchestrating multi-container applications with Docker Compose
* Understanding Docker container networking and service-to-service DNS resolution
* Proving data persistence across container restarts
* Testing API behavior with `curl`
* Using Swagger UI for API testing
* Documenting and publishing backend projects with GitHub

## Project Status

The project now runs on PostgreSQL, containerized with Docker and orchestrated with Docker Compose. The full stack starts with a single command (`docker compose up`), and task data persists across both application restarts and full container restarts, backed by a named Docker volume.
