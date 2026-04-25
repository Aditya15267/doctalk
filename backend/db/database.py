import os
import aiosqlite

DB_PATH = os.getenv("SQLITE_DB_PATH")


def get_db() -> aiosqlite.Connection:
    """
    Return an aiosqlite connection context manager for the database.

    This is a plain (non-async) function — it returns the connection object
    without starting it. The caller must use it with `async with` so that
    aiosqlite manages the thread lifecycle correctly:

        async with get_db() as conn:
            ...

    Returns:
        An aiosqlite Connection ready to be used as an async context manager.
    """
    return aiosqlite.connect(DB_PATH)


async def init_db() -> None:
    """
    Create all database tables if they do not already exist.

    Safe to call on every server startup — uses IF NOT EXISTS so existing
    data is never overwritten. Should be called once from the FastAPI
    startup event in main.py.
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                filename    TEXT NOT NULL,
                pages       INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                status      TEXT NOT NULL DEFAULT 'ready'
            );

            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                session_id  TEXT NOT NULL,
                filename    TEXT NOT NULL,
                pages       INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                message_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            );

            CREATE TABLE IF NOT EXISTS citations (
                citation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id   INTEGER NOT NULL,
                document_id  TEXT NOT NULL,
                chunk_text   TEXT NOT NULL,
                page_number  INTEGER NOT NULL,
                chunk_index  INTEGER NOT NULL,
                score        REAL NOT NULL,
                FOREIGN KEY (message_id) REFERENCES messages (message_id)
            );
        """)
        await conn.commit()
