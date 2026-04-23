import os
import aiosqlite

DB_PATH = os.getenv("SQLITE_DB_PATH")


async def get_db() -> aiosqlite.Connection:
    """
    Open and return an async SQLite connection.

    Reads the database path from the SQLITE_DB_PATH environment variable.
    Row factory is set so that query results are returned as dicts instead of plain tuples.

    Returns:
        An open aiosqlite connection. Caller is responsible for closing it.
    """
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    return conn


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
                chunk_text   TEXT NOT NULL,
                page_number  INTEGER NOT NULL,
                chunk_index  INTEGER NOT NULL,
                score        REAL NOT NULL,
                FOREIGN KEY (message_id) REFERENCES messages (message_id)
            );
        """)
        await conn.commit()
