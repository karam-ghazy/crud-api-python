from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

import repositories.postgres_task_repository as repo

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks, built as a learning project.",
    version="1.0",
)


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
    description="Returns all tasks stored in PostgreSQL."
)
def get_tasks():
    return repo.get_all_tasks()

@app.get(
    "/tasks/{id}",
    summary="Get a single task",
    description="Returns one task matching the given ID. Returns 404 if no task with that ID exists."
)
def get_task(id: int):
    task = repo.get_task(id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return task

@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a new task and stores it in PostgreSQL. Returns 400 if the title is missing or empty."
)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title must not be empty"
        )

    return repo.create_task(task.title)

@app.put(
    "/tasks/{id}",
    summary="Update a task",
    description="Updates a task's title and/or done status in PostgreSQL."
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

    updated = repo.update_task(id, update.title, update.done)

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return updated


@app.delete(
    "/tasks/{id}",
    status_code=204,
    summary="Delete a task",
    description="Permanently removes a task from PostgreSQL."
)
def delete_task(id: int):
    deleted = repo.delete_task(id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return Response(status_code=204)