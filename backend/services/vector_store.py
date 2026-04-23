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
        path = os.getenv("CHROMA_PERSIST_DIR")
        _client = chromadb.PersistentClient(path=path)
    return _client


def store_chunks(session_id: str, chunks: list[dict]) -> None:
    """
    Store embedded chunks into a ChromaDB collection named after the session.

    Creates a new collection for the session (or resets it if one already exists)
    and adds all chunks in a single batch. Each chunk must already have an
    "embedding" key from embed_chunks().

    Args:
        session_id: Unique identifier for the upload session. Used as the
                    collection name so each PDF's chunks are isolated.
        chunks: List of chunk dicts, each containing "text", "chunk_index",
                "page_number", and "embedding" keys.
    """
    client = get_client()
    collection = client.get_or_create_collection(name=session_id)

    collection.add(
        ids=[f"chunk_{chunk['chunk_index']}" for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[
            {
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
            }
            for chunk in chunks
        ],
    )


def search_chunks(session_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """
    Find the most semantically similar chunks to a query vector.

    Queries the ChromaDB collection for the given session and returns the
    top_k chunks whose embeddings are closest to the query embedding.
    Results are returned in order of relevance (most similar first).

    Args:
        session_id: The session whose ChromaDB collection to search.
        query_embedding: The embedded user question as a list of 384 floats,
                         produced by embed_query().
        top_k: Number of most similar chunks to return. Defaults to 5.

    Returns:
        A list of dicts, each containing:
            - text (str): The raw chunk text.
            - page_number (int): Page the chunk came from.
            - chunk_index (int): Position of the chunk in the document.
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
            "score": score,
        })

    return chunks


def delete_session(session_id: str) -> None:
    """
    Delete a session's ChromaDB collection and all its stored chunks.

    Used for cleanup when a session is no longer needed. Silently does
    nothing if the collection does not exist, so it is safe to call
    even if the session was never fully ingested.

    Args:
        session_id: The session whose collection should be deleted.
    """
    client = get_client()
    try:
        client.delete_collection(name=session_id)
    except Exception:
        pass
