from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

from config import settings


def connect():
    return psycopg.connect(settings.database_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id SERIAL PRIMARY KEY, "
            "author TEXT NOT NULL, "
            "text TEXT NOT NULL, "
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        conn.commit()
    yield


app = FastAPI(
    title="Guestbook",
    version="0.1.0",
    lifespan=lifespan,
)


class Message(BaseModel):
    author: str
    text: str


@app.get("/")
def index():
    return {"message": settings.greeting}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/messages")
def list_messages():
    with connect() as conn:
        rows = conn.execute(
            "SELECT author, text, created_at FROM messages "
            "ORDER BY id DESC"
        ).fetchall()
    return [
        {"author": author, "text": text, "created_at": created_at}
        for author, text, created_at in rows
    ]


@app.post("/messages")
def add_message(message: Message):
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages (author, text) VALUES (%s, %s)",
            (message.author, message.text),
        )
        conn.commit()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
    )