import aiosqlite
from db.database import get_db


async def save_message(session_id: str, role: str, content: str) -> int:
    """
    Insert a chat message and return its auto-generated ID.

    The returned message_id is needed to associate citations with this
    message immediately after saving.

    Args:
        session_id: The session this message belongs to.
        role: Either "user" or "assistant".
        content: The full text of the message.

    Returns:
        The auto-incremented message_id assigned by SQLite.
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (session_id, role, content),
        )
        await conn.commit()
        return cursor.lastrowid


async def save_citations(message_id: int, citations: list[dict]) -> None:
    """
    Insert citation records linked to an assistant message.

    Each citation represents a chunk retrieved from ChromaDB that was
    used as context when generating the assistant's response.

    Args:
        message_id: The ID of the assistant message these citations belong to.
        citations: List of dicts from search_chunks(), each containing
                   "text", "page_number", "chunk_index", and "score".
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        await conn.executemany(
            """
            INSERT INTO citations (message_id, chunk_text, page_number, chunk_index, score)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    message_id,
                    citation["text"],
                    citation["page_number"],
                    citation["chunk_index"],
                    citation["score"],
                )
                for citation in citations
            ],
        )
        await conn.commit()


async def get_history(session_id: str) -> list[dict]:
    """
    Retrieve all messages and their citations for a session.

    Fetches messages in chronological order. For each assistant message,
    the associated citations are fetched and attached. User messages
    always have an empty citations list.

    Args:
        session_id: The session to retrieve history for.

    Returns:
        A list of message dicts ordered by created_at, each containing:
            - role (str): "user" or "assistant".
            - content (str): The message text.
            - created_at (str): ISO timestamp.
            - citations (list[dict]): Source chunks (empty for user messages).
    """
    async with get_db() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            """
            SELECT message_id, role, content, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        ) as cursor:
            messages = [dict(row) for row in await cursor.fetchall()]

        for message in messages:
            if message["role"] == "assistant":
                async with conn.execute(
                    """
                    SELECT chunk_text, page_number, chunk_index, score
                    FROM citations
                    WHERE message_id = ?
                    """,
                    (message["message_id"],),
                ) as cursor:
                    message["citations"] = [dict(row) for row in await cursor.fetchall()]
            else:
                message["citations"] = []

        return messages
