from services.pdf_processor import extract_text, chunk_text
from services.embedder import embed_chunks
from services.vector_store import store_chunks


def ingest_pdf(session_id: str, document_id: str, file_bytes: bytes) -> dict:
    """
    Run the full PDF ingestion pipeline for a document within a session.

    Orchestrates the four steps in sequence: extract text per page, split
    into overlapping chunks with real page numbers, embed each chunk into
    a vector, and store everything in ChromaDB tagged with the document_id.

    Args:
        session_id: Unique identifier for the workspace. Used to namespace
                    the ChromaDB collection so all documents in a session
                    are searchable together.
        document_id: Unique identifier for this specific PDF within the
                     session. Stored in each chunk's metadata so citations
                     know which document they came from.
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        A dict with:
            - chunks (int): Total number of chunks stored in ChromaDB.
            - pages (int): Total number of pages in the PDF.
    """
    pages = extract_text(file_bytes)
    chunks = chunk_text(pages)
    chunks = embed_chunks(chunks)
    store_chunks(session_id, document_id, chunks)

    return {"chunks": len(chunks), "pages": len(pages)}
