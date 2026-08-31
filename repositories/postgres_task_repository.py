"""
postgres_task_repository.py
----------------------------
PostgreSQL implementation of task storage.

This module is a drop-in replacement for the sqlite3 calls currently
inlined in main.py. It exposes the same operations, with the same
inputs and the same return shapes (plain dicts with "id"/"title"/"done",
or None/False when a task isn't found) that main.py's routes already
work with today for SQLite.

Nothing in this file is wired into main.py yet -- that happens in
Stage 4. This file can be dropped in unchanged when that happens.
"""

import os
from typing import Optional

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    Open a new PostgreSQL connection using the URL from .env.

    A fresh connection per call mirrors main.py's current
    sqlite3.connect(DATABASE) pattern -- each operation opens, uses, and
    closes its own connection. This keeps the repository directly
    comparable to the SQLite version, rather than introducing a new
    concept (like a connection pool) in the same stage as the
    repository itself.
    """
    if DATABASE_URL is None:
        raise RuntimeError(
            "DATABASE_URL is not set. Check that .env exists and "
            "contains a DATABASE_URL value."
        )
    return psycopg2.connect(DATABASE_URL)


def _row_to_task(row) -> dict:
    """Convert a (id, title, done) row into the dict shape the API expects."""
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


def get_all_tasks() -> list[dict]:
    """Return every task, ordered by id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, done FROM tasks ORDER BY id")
        rows = cursor.fetchall()
        return [_row_to_task(row) for row in rows]
    finally:
        connection.close()


def get_task(task_id: int) -> Optional[dict]:
    """Return one task by id, or None if it doesn't exist."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, title, done FROM tasks WHERE id = %s",
            (task_id,),
        )
        row = cursor.fetchone()
        return _row_to_task(row) if row is not None else None
    finally:
        connection.close()


def create_task(title: str) -> dict:
    """
    Insert a new task with done=False and return the created row.

    Title validation (empty/whitespace check) stays in main.py, exactly
    like it does today -- this repository only persists what it's
    given, it does not validate.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) "
            "RETURNING id, title, done",
            (title, False),
        )
        row = cursor.fetchone()
        connection.commit()
        return _row_to_task(row)
    finally:
        connection.close()


def update_task(
    task_id: int, title: Optional[str], done: Optional[bool]
) -> Optional[dict]:
    """
    Update a task's title and/or done status.

    Returns the updated task, or None if no task with that id exists.
    Like create_task, this assumes the caller (main.py) has already
    validated the incoming values.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, title, done FROM tasks WHERE id = %s",
            (task_id,),
        )
        existing = cursor.fetchone()
        if existing is None:
            return None

        new_title = title if title is not None else existing[1]
        new_done = done if done is not None else bool(existing[2])

        cursor.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s "
            "RETURNING id, title, done",
            (new_title, new_done, task_id),
        )
        updated_row = cursor.fetchone()
        connection.commit()
        return _row_to_task(updated_row)
    finally:
        connection.close()


def delete_task(task_id: int) -> bool:
    """
    Delete a task by id.

    Returns True if a task was deleted, False if no task with that id
    existed -- so the caller can decide whether to raise a 404, exactly
    as main.py does today for SQLite.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id",
            (task_id,),
        )
        deleted_row = cursor.fetchone()
        connection.commit()
        return deleted_row is not None
    finally:
        connection.close()