from fastapi import APIRouter, HTTPException

from db.message_store import get_history
from db.session_store import get_session
from models.schemas import HistoryResponse, MessageSchema, CitationSchema

router = APIRouter()


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def history(session_id: str):
    """
    Retrieve the full chat history for a session.

    Fetches all messages and their citations from SQLite in chronological
    order. Returns a 404 if the session does not exist.

    Args:
        session_id: The session ID from the URL path.

    Returns:
        HistoryResponse containing the session_id and list of messages.

    Raises:
        HTTPException 404: If the session_id is not found in SQLite.
    """
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    messages = await get_history(session_id)

    return HistoryResponse(
        session_id=session_id,
        messages=[
            MessageSchema(
                role=message["role"],
                content=message["content"],
                created_at=message["created_at"],
                citations=[
                    CitationSchema(**citation)
                    for citation in message["citations"]
                ],
            )
            for message in messages
        ],
    )
