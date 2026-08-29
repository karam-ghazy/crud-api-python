from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import sqlite3

app = FastAPI(
    title="Task API",
    description="A simple in-memory CRUD API for managing tasks, built as a learning project.",
    version="1.0",
)

DATABASE = "tasks.db"

def init_db():
    
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    cursor = connection.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        connection.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", False),
                ("Build CRUD API", False),
                ("Learn SQLite", True),
            ],
        )
        
    connection.commit()
    connection.close()

init_db()

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None



@app.get("/", summary="API info", description="Returns basic metadata about this API, including its name, version, and available resource endpoints.")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check", description="Returns a simple status indicating the server is running. Used for uptime/liveness checks.")
def health_check():
    return {"status": "ok"}

@app.get(
    "/tasks",
    summary="List all tasks",
    description="Returns all tasks stored in the SQLite database."
)
def get_tasks():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        "SELECT id, title, done FROM tasks"
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2]),
        }
        for row in rows
    ]

@app.get(
    "/tasks/{id}",
    summary="Get a single task",
    description="Returns one task matching the given ID. Returns 404 if no task with that ID exists."
)
def get_task(id: int):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }

@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a new task and stores it in the SQLite database. Returns 400 if the title is missing or empty."
)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title must not be empty"
        )

    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, False)
    )

    task_id = cursor.lastrowid

    connection.commit()

    cursor = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    connection.close()

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }

@app.put(
    "/tasks/{id}",
    summary="Update a task",
    description="Updates a task's title and/or done status in the SQLite database."
)
def update_task(id: int, update: TaskUpdate):
    if update.title is None and update.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body must include title and/or done"
        )

    if update.title is not None and not update.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title must not be empty"
        )

    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    new_title = update.title if update.title is not None else row[1]
    new_done = update.done if update.done is not None else bool(row[2])

    connection.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, id)
    )

    connection.commit()

    cursor = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (id,)
    )

    updated_row = cursor.fetchone()

    connection.close()

    return {
        "id": updated_row[0],
        "title": updated_row[1],
        "done": bool(updated_row[2]),
    }


@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete a task",
    description="Permanently removes a task from the SQLite database."
)
def delete_task(id: int):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return Response(status_code=204)