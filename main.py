from datetime import datetime, timezone
import sqlite3
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

APP_NAME = "AgentGuard"
DB_PATH = Path("agentguard.db")

app = FastAPI(
    title=APP_NAME,
    description="Lightweight local security monitoring layer.",
    version="0.1.0",
)


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        connection.commit()


def log_event(event_type: str, source: str, message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO events (timestamp, event_type, source, message)
            VALUES (?, ?, ?, ?)
            """,
            (timestamp, event_type, source, message),
        )
        connection.commit()


class Event(BaseModel):
    event_type: str
    source: str
    message: str


@app.on_event("startup")
def startup() -> None:
    init_db()
    log_event(
        "startup",
        "agentguard",
        "Monitoring service started",
    )


@app.get("/")
def root() -> dict:
    return {
        "name": APP_NAME,
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "service": APP_NAME,
    }


@app.post("/events")
def create_event(event: Event) -> dict:
    log_event(
        event.event_type,
        event.source,
        event.message,
    )

    return {
        "status": "recorded",
        "event_type": event.event_type,
    }


@app.get("/events")
def get_events(limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 500))

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT id, timestamp, event_type, source, message
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]
        
    
