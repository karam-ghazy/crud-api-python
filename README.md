# Task API

A simple in-memory CRUD API for managing tasks, built with FastAPI as a backend engineering learning project.

## Description

This project implements a complete CRUD (Create, Read, Update, Delete) REST API for a task list. It was built incrementally, stage by stage, covering server setup, endpoint design, input validation, proper HTTP status codes, and interactive API documentation via Swagger UI. Data is stored in memory only — no database is used.

## Technologies Used

- Python 3.10+
- FastAPI
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Swagger UI (auto-generated interactive docs)

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The server will be available at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint         | Description                                  |
|--------|------------------|-----------------------------------------------|
| GET    | `/`              | Returns API name, version, and endpoint list |
| GET    | `/health`        | Returns server health status                 |
| GET    | `/tasks`         | Returns all tasks                            |
| GET    | `/tasks/{id}`    | Returns a single task by ID                  |
| POST   | `/tasks`         | Creates a new task                           |
| PUT    | `/tasks/{id}`    | Updates a task's title and/or done status    |
| DELETE | `/tasks/{id}`    | Deletes a task                               |

## Example Usage

**Request:**
```bash
curl -i http://localhost:8000/tasks
```

**Response:**
```
HTTP/1.1 200 OK
content-type: application/json

[
  {"id":1,"title":"Learn FastAPI","done":false},
  {"id":2,"title":"Build a CRUD API","done":false},
  {"id":3,"title":"Write tests","done":true}
]
```

**Creating a task:**
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

**Response:**
```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Interactive Documentation (Swagger UI)

FastAPI automatically generates interactive API docs. With the server running, visit:

**http://localhost:8000/docs**

From there you can view every endpoint and execute real requests directly in the browser using "Try it out."

![Swagger UI screenshot](docs/swagger-screenshot.png)

*(Screenshot: add your saved Swagger UI screenshot to a `docs/` folder in the repo and reference it here — replace the path above if you name the file or folder differently.)*

## Important Behavior

- **In-memory storage:** All task data is stored in a Python list in server memory. Nothing is written to disk.
- **Data resets on restart:** Every time the server restarts, the task list resets to its original 3 seed tasks. Anything created, updated, or deleted during a session is lost.
- **Validation rules:**
  - `POST /tasks` requires a non-empty `title`. An empty/whitespace title returns `400`; a missing `title` field returns `422`.
  - `PUT /tasks/{id}` requires at least one of `title` or `done` in the request body; an empty body returns `400`. If `title` is provided, it cannot be empty.
- **HTTP status codes:**

  | Status | Meaning                                          |
  |--------|---------------------------------------------------|
  | 200    | Successful GET or PUT                              |
  | 201    | Successful POST (resource created)                 |
  | 204    | Successful DELETE (no content returned)            |
  | 400    | Invalid request body (e.g. empty title)            |
  | 404    | Task ID not found                                  |
  | 422    | Request body missing a required field (Pydantic)   |
