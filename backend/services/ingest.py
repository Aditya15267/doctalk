import io
import pdfplumber

from services.pdf_processor import extract_text, chunk_text
from services.embedder import embed_chunks
from services.vector_store import store_chunks


def ingest_pdf(session_id: str, file_bytes: bytes) -> dict:
    """
    Run the full PDF ingestion pipeline for a given session.

    Orchestrates the four steps in sequence: extract text from the PDF,
    split into overlapping chunks, embed each chunk into a vector, and
    store everything in ChromaDB under the session's collection.

    Args:
        session_id: Unique identifier for this upload session. Used to
                    namespace the ChromaDB collection.
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        A dict with:
            - chunks (int): Total number of chunks stored in ChromaDB.
            - pages (int): Total number of pages in the PDF.
    """
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)

    text = extract_text(file_bytes)
    chunks = chunk_text(text)
    chunks = embed_chunks(chunks)
    store_chunks(session_id, chunks)

    return {"chunks": len(chunks), "pages": page_count}
