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
    title: str

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

@app.post("/tasks", status_code=201, summary="Create a task", description="Creates a new task with the given title. `done` is always set to false on creation. Returns 400 if the title is missing or empty.")
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title must not be empty")

    new_task = {
        "id": get_next_id(),
        "title": task.title,
        "done": False,
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{id}", summary="Update a task", description="Updates a task's title and/or done status. At least one field must be provided. Returns 404 if the task doesn't exist, 400 for invalid input.")
def update_task(id: int, update: TaskUpdate):
    task = None
    for t in tasks:
        if t["id"] == id:
            task = t
            break

    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    if update.title is None and update.done is None:
        raise HTTPException(status_code=400, detail="Request body must include title and/or done")

    if update.title is not None and not update.title.strip():
        raise HTTPException(status_code=400, detail="Title must not be empty")

    if update.title is not None:
        task["title"] = update.title
    if update.done is not None:
        task["done"] = update.done

    return task

@app.delete("/tasks/{id}", status_code=204, summary="Delete a task", description="Permanently removes a task from the in-memory list. Returns 404 if the task doesn't exist.")
def delete_task(id: int):
    task = None
    for t in tasks:
        if t["id"] == id:
            task = t
            break

    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    tasks.remove(task)
    return Response(status_code=204)
