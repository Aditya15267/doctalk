import io
import pdfplumber


def extract_text(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF given its raw bytes.

    Loops through every page using pdfplumber and skips pages that return
    no text (e.g. blank pages or image-only scans). All pages are joined
    into a single string separated by newlines.

    Args:
        file_bytes: Raw bytes of the PDF file, as received from an upload.

    Returns:
        A single plain text string containing all extractable text from the PDF.
    """
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Split a plain text string into overlapping word-based chunks.

    Each chunk slides forward by (chunk_size - overlap) words so that
    context is preserved across chunk boundaries. For example, with
    chunk_size=500 and overlap=50, chunk 2 starts 50 words before
    chunk 1 ends — preventing answers from being split across chunks.

    Args:
        text: Plain text string to split, typically from extract_text().
        chunk_size: Number of words per chunk. Defaults to 500.
        overlap: Number of words repeated between consecutive chunks. Defaults to 50.

    Returns:
        A list of dicts, each with:
            - text (str): The chunk's word content joined back into a string.
            - chunk_index (int): Position of this chunk in the sequence (0-based).
            - page_number (int): Placeholder — populated at the vector store stage.
    """
    words = text.split()
    step = chunk_size - overlap
    chunks = []

    for i, start in enumerate(range(0, len(words), step)):
        chunk_words = words[start : start + chunk_size]
        chunks.append({
            "text": " ".join(chunk_words),
            "chunk_index": i,
            "page_number": 0,
        })

    return chunks