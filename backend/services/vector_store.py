import os
import chromadb

_client = None


def get_client() -> chromadb.PersistentClient:
    """
    Create a ChromaDB persistent client once and reuse it for the lifetime of the process.

    Reads the storage path from the CHROMA_PERSIST_DIR environment variable,
    falling back to ./chroma_data if not set.

    Returns:
        A ChromaDB PersistentClient instance connected to the local vector store.
    """
    global _client
    if _client is None:
        path = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        _client = chromadb.PersistentClient(path=path)
    return _client


def store_chunks(session_id: str, document_id: str, chunks: list[dict]) -> None:
    """
    Store embedded chunks into the session's ChromaDB collection.

    All documents in a session share one collection. Each chunk is tagged
    with document_id in its metadata so cross-document search results can
    identify which document they came from.

    Args:
        session_id: Workspace identifier — used as the collection name.
        document_id: Identifier for the specific PDF these chunks belong to.
        chunks: List of chunk dicts with "text", "chunk_index", "page_number",
                and "embedding" keys.
    """
    client = get_client()
    collection = client.get_or_create_collection(name=session_id)

    collection.add(
        ids=[f"{document_id}_chunk_{chunk['chunk_index']}" for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[
            {
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "document_id": document_id,
            }
            for chunk in chunks
        ],
    )


def search_chunks(session_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """
    Find the most semantically similar chunks across all documents in a session.

    Searches the entire session collection so results can come from any
    document in the workspace — enabling cross-document questions.
    Results are returned in order of relevance (most similar first).

    Args:
        session_id: The workspace whose ChromaDB collection to search.
        query_embedding: The embedded user question as a list of 384 floats,
                         produced by embed_query().
        top_k: Number of most similar chunks to return. Defaults to 5.

    Returns:
        A list of dicts, each containing:
            - text (str): The raw chunk text.
            - page_number (int): Page the chunk came from.
            - chunk_index (int): Position of the chunk in the document.
            - document_id (str): Which document this chunk belongs to.
            - score (float): Similarity score (lower = more similar in ChromaDB).
    """
    client = get_client()
    collection = client.get_collection(name=session_id)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, metadata, score in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "page_number": metadata["page_number"],
            "chunk_index": metadata["chunk_index"],
            "document_id": metadata["document_id"],
            "score": score,
        })

    return chunks


def delete_document(session_id: str, document_id: str) -> None:
    """
    Delete all chunks belonging to a specific document from the session collection.

    Used when a document is removed from a workspace. The collection itself
    is kept — other documents in the session are unaffected.

    Args:
        session_id: The workspace collection to search within.
        document_id: The document whose chunks should be deleted.
    """
    client = get_client()
    try:
        collection = client.get_collection(name=session_id)
        collection.delete(where={"document_id": document_id})
    except Exception:
        pass


def delete_session(session_id: str) -> None:
    """
    Delete the entire session collection and all its stored chunks.

    Used for cleanup when a workspace is no longer needed. Silently does
    nothing if the collection does not exist.

    Args:
        session_id: The session whose collection should be deleted.
    """
    client = get_client()
    try:
        client.delete_collection(name=session_id)
    except Exception:
        pass
