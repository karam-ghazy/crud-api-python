# Task API

A simple CRUD REST API for managing tasks, built with Python, FastAPI, and SQLite as a backend engineering learning project.

## Description

This project implements a complete CRUD (Create, Read, Update, Delete) REST API for managing a task list.

The project was originally built with in-memory storage and then extended to use a real SQLite database. The API endpoints, request formats, validation rules, and HTTP status codes remain the same, while the storage layer was replaced with persistent database storage.

The main goal of this iteration was to understand the separation between the **API layer** and the **data layer**.

The architecture is now:

```text
Client
   |
   v
FastAPI
   |
   v
sqlite3
   |
   v
SQLite (tasks.db)
```

Unlike the previous in-memory implementation, task data now survives when the server is restarted.

## Technologies Used

* Python 3.10+
* FastAPI
* Uvicorn
* Pydantic
* SQLite
* Python `sqlite3`
* Swagger UI
* Git & GitHub

## Project Structure

```text
task-api/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── docs/
    └── database-screenshot.png
```

The SQLite database file is:

```text
tasks.db
```

It is generated automatically by the application and does not need to be manually created.

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
python3 -m venv venv
```

Activate the virtual environment on Linux/macOS:

```bash
source venv/bin/activate
```

On Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Start the FastAPI development server with:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

Interactive Swagger documentation is available at:

```text
http://localhost:8000/docs
```

## Database

This version of the project uses **SQLite** instead of an in-memory Python list.

SQLite was chosen because it is lightweight, requires no separate database server, and stores the application's data in a single file.

The database file is:

```text
tasks.db
```

The application automatically:

1. Creates `tasks.db` if it does not exist.
2. Creates the `tasks` table if it does not exist.
3. Inserts three example tasks when the table is empty.

The database table contains the following columns:

| Column  | Type    | Description                            |
| ------- | ------- | -------------------------------------- |
| `id`    | INTEGER | Unique task identifier and primary key |
| `title` | TEXT    | Task title                             |
| `done`  | BOOLEAN | Whether the task is completed          |

## Database Persistence

The previous version stored tasks in server memory.

That meant that restarting the server removed any tasks created during the previous session.

The new implementation stores tasks in SQLite:

```text
Previous:

FastAPI → Python List

Current:

FastAPI → sqlite3 → SQLite
```

Because the data is stored in `tasks.db`, tasks remain available after restarting the server.

For example:

```text
Create task
    ↓
POST /tasks
    ↓
SQLite
    ↓
tasks.db
    ↓
Restart server
    ↓
GET /tasks
    ↓
Task still exists
```

This demonstrates persistence and separates the API behavior from the underlying storage implementation.

## API Endpoints

| Method | Endpoint      | Description                                         |
| ------ | ------------- | --------------------------------------------------- |
| GET    | `/`           | Returns API name, version, and endpoint information |
| GET    | `/health`     | Returns server health status                        |
| GET    | `/tasks`      | Returns all tasks from SQLite                       |
| GET    | `/tasks/{id}` | Returns a single task by ID                         |
| POST   | `/tasks`      | Creates a new task in SQLite                        |
| PUT    | `/tasks/{id}` | Updates an existing task                            |
| DELETE | `/tasks/{id}` | Deletes a task                                      |

The API endpoints remain the same as the previous CRUD implementation. Only the storage layer has changed.

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
  },
  {
    "id": 3,
    "title": "Learn SQLite",
    "done": true
  }
]
```

### Get a Single Task

```bash
curl -i http://localhost:8000/tasks/1
```

Example response:

```text
HTTP/1.1 200 OK
content-type: application/json
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

Example response:

```text
HTTP/1.1 201 Created
content-type: application/json
```

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

The new task is inserted into the SQLite database.

### Update a Task

```bash
curl -i -X PUT http://localhost:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

Example response:

```text
HTTP/1.1 200 OK
content-type: application/json
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

Example response:

```text
HTTP/1.1 204 No Content
```

The task is removed from the SQLite database.

## Validation Rules

The API validates incoming data before modifying the database.

### POST `/tasks`

The `title` field is required and cannot be empty or contain only whitespace.

Example invalid request:

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```

The API returns:

```text
400 Bad Request
```

### PUT `/tasks/{id}`

At least one of the following fields must be provided:

```json
{
  "title": "...",
  "done": true
}
```

An empty update body returns:

```text
400 Bad Request
```

If a `title` is provided, it cannot be empty or contain only whitespace.

## HTTP Status Codes

| Status | Meaning                                                               |
| ------ | --------------------------------------------------------------------- |
| 200    | Successful GET or PUT request                                         |
| 201    | Task successfully created                                             |
| 204    | Task successfully deleted                                             |
| 400    | Invalid request body                                                  |
| 404    | Task ID not found                                                     |
| 422    | Request body is missing a required field or fails Pydantic validation |

## Error Handling

If a requested task does not exist, the API returns a `404` response.

Example:

```bash
curl -i http://localhost:8000/tasks/99
```

Example response:

```json
{
  "detail": "Task 99 not found"
}
```

The API does not return an empty successful response for an unknown task ID.

## Working Directly With SQLite

As part of the database implementation, SQLite was also explored directly using SQL queries.

### List all tasks

```sql
SELECT * FROM tasks;
```

### Show completed tasks

```sql
SELECT * FROM tasks WHERE done = 1;
```

### Count all tasks

```sql
SELECT COUNT(*) FROM tasks;
```

### Mark all tasks as completed

```sql
UPDATE tasks SET done = 1;
```

### Delete completed tasks

```sql
DELETE FROM tasks WHERE done = 1;
```

These queries were executed directly against the SQLite database to understand how SQL operations affect the data used by the API.

Changes made directly to the database can then be observed through:

```bash
curl -i http://localhost:8000/tasks
```

This demonstrates that the API and database are working with the same persistent data.

## Database Screenshot

The SQLite database was inspected using a SQLite database viewer.

![SQLite Database](docs/database-screenshot.png)

The screenshot shows the `tasks` table and its stored task records.

## Interactive Documentation — Swagger UI

FastAPI automatically generates interactive API documentation using Swagger UI.

With the server running, open:

```text
http://localhost:8000/docs
```

Swagger UI provides access to all API endpoints and allows requests to be executed directly through the browser using **Try it out**.

![Swagger UI](docs/swagger-screenshot.png)

## CRUD Flow

The complete CRUD cycle is:

```text
CREATE
POST /tasks
      ↓
SQLite INSERT
      ↓
READ
GET /tasks
      ↓
UPDATE
PUT /tasks/{id}
      ↓
SQLite UPDATE
      ↓
DELETE
DELETE /tasks/{id}
      ↓
SQLite DELETE
```

All operations use the same API interface while the actual data is stored in SQLite.

## What Changed From Week 2

### Week 2

Tasks were stored in memory:

```text
FastAPI → Python List
```

This meant that restarting the server removed changes made during the session.

### Week 3

Tasks are stored in SQLite:

```text
FastAPI → sqlite3 → tasks.db
```

The API endpoints and their behavior remain the same, but the data is now persistent.

This shows an important backend engineering concept:

> The API defines what the application does, while the data layer defines where the application stores its data.

## Learning Outcomes

Through this project, I practiced:

* Building REST API endpoints with FastAPI
* Implementing CRUD operations
* Using HTTP methods correctly
* Handling HTTP status codes
* Validating request data with Pydantic
* Connecting FastAPI to SQLite
* Creating database tables programmatically
* Executing SQL queries with Python `sqlite3`
* Reading, inserting, updating, and deleting database records
* Understanding persistent data storage
* Testing API behavior with `curl`
* Using Swagger UI for API testing
* Documenting and publishing backend projects with GitHub

## Project Status

The Week 3 database implementation is complete.

The API now uses SQLite for persistent task storage while maintaining the same CRUD interface developed in the previous version.
