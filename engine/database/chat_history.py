"""
SQLite-backed chat history storage for DeepContext.
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass(frozen=True)
class SessionRecord:
    id: str
    title: str
    created_at: str


@dataclass(frozen=True)
class MessageRecord:
    id: int
    session_id: str
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]]
    created_at: str


class ChatHistoryStore:
    """SQLite storage for chat sessions and messages."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            db_path = Path(__file__).resolve().parent / "chat_history.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)"
            )
            conn.commit()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_session(self, title: Optional[str] = None) -> SessionRecord:
        session_id = uuid4().hex
        session_title = title or "新对话"
        created_at = self._now_iso()

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
                (session_id, session_title, created_at),
            )
            conn.commit()

        return SessionRecord(id=session_id, title=session_title, created_at=created_at)

    def list_sessions(self) -> List[SessionRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, created_at FROM sessions ORDER BY created_at DESC"
            ).fetchall()

        return [SessionRecord(**dict(row)) for row in rows]

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, created_at FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()

        return SessionRecord(**dict(row)) if row else None

    def delete_session(self, session_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> MessageRecord:
        created_at = self._now_iso()
        sources_json = (
            json.dumps(sources, ensure_ascii=False) if sources is not None else None
        )

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (session_id, role, content, sources, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, sources_json, created_at),
            )
            conn.commit()
            message_id = cursor.lastrowid

        return MessageRecord(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            created_at=created_at,
        )

    def list_messages(self, session_id: str) -> List[MessageRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, sources, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        messages: List[MessageRecord] = []
        for row in rows:
            data = dict(row)
            sources_value = data.get("sources")
            sources = json.loads(sources_value) if sources_value else None
            messages.append(
                MessageRecord(
                    id=data["id"],
                    session_id=data["session_id"],
                    role=data["role"],
                    content=data["content"],
                    sources=sources,
                    created_at=data["created_at"],
                )
            )
        return messages


_chat_history_store: Optional[ChatHistoryStore] = None


def get_chat_history(db_path: Optional[Path] = None) -> ChatHistoryStore:
    global _chat_history_store
    if _chat_history_store is None:
        _chat_history_store = ChatHistoryStore(db_path=db_path)
    return _chat_history_store
