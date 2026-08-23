from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

# ⚠️ Пока всё зашито прямо в код — это и предстоит исправить.
DATABASE_URL = "postgresql://guestbook:supersecret123@localhost:5432/guestbook"
GREETING = "Добро пожаловать в гостевую книгу!"


def connect():
    return psycopg.connect(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id SERIAL PRIMARY KEY, author TEXT, text TEXT)"
        )
    yield


app = FastAPI(lifespan=lifespan)


class Message(BaseModel):
    author: str
    text: str


@app.get("/")
def index():
    return {"message": GREETING}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/messages")
def list_messages():
    with connect() as conn:
        rows = conn.execute(
            "SELECT author, text FROM messages ORDER BY id DESC"
        ).fetchall()
    return [{"author": author, "text": text} for author, text in rows]


@app.post("/messages")
def add_message(message: Message):
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages (author, text) VALUES (%s, %s)",
            (message.author, message.text),
        )
    return {"ok": True}
