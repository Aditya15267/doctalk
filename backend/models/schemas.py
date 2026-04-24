from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Response returned after a PDF is successfully uploaded and ingested."""
    session_id: str
    filename: str
    pages: int
    chunks: int
    status: str


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    session_id: str
    question: str


class CitationSchema(BaseModel):
    """A single source chunk referenced in an assistant message."""
    chunk_text: str
    page_number: int
    chunk_index: int
    score: float


class MessageSchema(BaseModel):
    """A single chat message with its associated citations."""
    role: str
    content: str
    created_at: str
    citations: list[CitationSchema]


class HistoryResponse(BaseModel):
    """Full chat history for a session."""
    session_id: str
    messages: list[MessageSchema]
