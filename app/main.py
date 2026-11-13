import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "tasks.db"
STATIC_DIR = BASE_DIR / "static"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )"""
        )
    yield


app = FastAPI(title="EC2 Practice App", lifespan=lifespan)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tasks")
def list_tasks():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]


@app.post("/api/tasks", status_code=201)
def create_task(task: TaskIn):
    title = task.title.strip()
    with get_db() as conn:
        cur = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        new_id = cur.lastrowid
    return {"id": new_id, "title": title, "done": False}


@app.patch("/api/tasks/{task_id}")
def toggle_task(task_id: int):
    with get_db() as conn:
        cur = conn.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Task not found")
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Task not found")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
