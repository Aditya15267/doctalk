import aiosqlite
from db.database import get_db


async def create_document(
    session_id: str,
    document_id: str,
    filename: str,
    pages: int,
    chunk_count: int,
) -> None:
    """
    Insert a new document record into the documents table.

    Called after a PDF is successfully ingested into a session so the
    document is available for listing and citation lookups.

    Args:
        session_id: The workspace this document belongs to.
        document_id: Unique identifier for this specific PDF (UUID).
        filename: Original name of the uploaded PDF file.
        pages: Total number of pages in the PDF.
        chunk_count: Number of chunks stored in ChromaDB for this document.
    """
    async with get_db() as conn:
        await conn.execute(
            """
            INSERT INTO documents (document_id, session_id, filename, pages, chunk_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, session_id, filename, pages, chunk_count),
        )
        await conn.commit()


async def list_documents(session_id: str) -> list[dict]:
    """
    Retrieve all documents belonging to a session, ordered by upload time.

    Args:
        session_id: The workspace whose documents to list.

    Returns:
        A list of dicts, each representing one document. Empty list if none.
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT * FROM documents WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_document(document_id: str) -> dict | None:
    """
    Retrieve a single document record by its ID.

    Args:
        document_id: The document ID to look up.

    Returns:
        A dict with document fields if found, or None if it does not exist.
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT * FROM documents WHERE document_id = ?",
            (document_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
