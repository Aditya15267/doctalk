from sentence_transformers import SentenceTransformer

_embedder = None


def get_embedder() -> SentenceTransformer:
    """
    Load the sentence embedding model once and reuse it for the lifetime of the process.

    Uses a module-level variable to ensure the model is only loaded on the first call.
    Subsequent calls return the already-loaded instance, avoiding the 3-5 second
    reload cost on every request.

    Returns:
        A loaded SentenceTransformer instance ready to encode text.
    """
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Add an embedding vector to each chunk dict.

    Extracts all chunk texts and encodes them in a single batch for efficiency.
    The resulting vectors are converted from numpy arrays to plain Python lists
    before being attached back to each chunk dict.

    Args:
        chunks: List of chunk dicts from chunk_text(), each containing
                at minimum a "text" key.

    Returns:
        The same list of dicts with an "embedding" key added to each,
        where the value is a list of 384 floats representing the chunk's meaning.
    """
    model = get_embedder()
    texts = [chunk["text"] for chunk in chunks]
    vectors = model.encode(texts)

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector.tolist()

    return chunks


def embed_query(query: str) -> list[float]:
    """
    Convert a user's question into an embedding vector.

    Uses the same model as embed_chunks() so that query vectors and chunk
    vectors live in the same mathematical space — a requirement for
    meaningful similarity comparison in ChromaDB.

    Args:
        query: The user's plain text question.

    Returns:
        A list of 384 floats representing the question's meaning as a vector.
    """
    model = get_embedder()
    return model.encode(query).tolist()
