import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from db.message_store import get_history, save_citations, save_message
from db.session_store import get_session
from models.schemas import ChatRequest
from services.embedder import embed_query
from services.llm import stream_answer
from services.vector_store import search_chunks

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Answer a question about the uploaded document using streaming SSE.

    Validates the session, retrieves relevant chunks from ChromaDB, streams
    Claude's response token by token, then persists the full exchange to SQLite.

    Args:
        request: ChatRequest containing session_id and question.

    Returns:
        A StreamingResponse of Server-Sent Events with token and done events.

    Raises:
        HTTPException 404: If the session_id does not exist in SQLite.
    """
    session = await get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    query_embedding = embed_query(request.question)
    chunks = search_chunks(request.session_id, query_embedding, top_k=5)

    await save_message(request.session_id, "user", request.question)

    async def event_generator():
        full_response = []

        async for token in stream_answer(request.question, chunks):
            full_response.append(token)
            yield f"data: {json.dumps({'type': 'token', 'value': token})}\n\n"

        assistant_message_id = await save_message(
            request.session_id, "assistant", "".join(full_response)
        )
        await save_citations(assistant_message_id, chunks)

        citations_payload = [
            {
                "chunk_text": c["text"],
                "page_number": c["page_number"],
                "chunk_index": c["chunk_index"],
                "score": c["score"],
            }
            for c in chunks
        ]
        yield f"data: {json.dumps({'type': 'done', 'citations': citations_payload})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
