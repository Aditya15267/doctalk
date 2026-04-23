import aiosqlite
from db.database import get_db


async def create_session(
    session_id: str,
    filename: str,
    pages: int,
    chunk_count: int,
) -> None:
    """
    Insert a new session record into the sessions table.

    Called immediately after a PDF is successfully ingested so the session
    is available for chat and history lookups.

    Args:
        session_id: Unique identifier for the session (UUID).
        filename: Original name of the uploaded PDF file.
        pages: Total number of pages in the PDF.
        chunk_count: Number of chunks stored in ChromaDB for this session.
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute(
            """
            INSERT INTO sessions (session_id, filename, pages, chunk_count)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, filename, pages, chunk_count),
        )
        await conn.commit()


async def get_session(session_id: str) -> dict | None:
    """
    Retrieve a session record by its ID.

    Args:
        session_id: The session ID to look up.

    Returns:
        A dict with session fields if found, or None if the session does not exist.
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (session_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
