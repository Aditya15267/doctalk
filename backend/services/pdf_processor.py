import io
import pdfplumber


def extract_text(file_bytes: bytes) -> list[str]:
    """
    Extract plain text from each page of a PDF given its raw bytes.

    Returns one string per page rather than a single joined string so that
    page numbers are preserved for accurate citations and the PDF viewer.
    Pages with no extractable text (blank or image-only) are returned as
    empty strings so the page index stays aligned with the PDF page numbers.

    Args:
        file_bytes: Raw bytes of the PDF file, as received from an upload.

    Returns:
        A list of strings, one per page. Index 0 = page 1.
    """
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            pages.append(text or "")

    return pages


def chunk_text(pages: list[str], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Split page-separated text into overlapping word-based chunks.

    Processes each page independently so chunk boundaries never cross page
    boundaries. This guarantees every chunk has an accurate page_number.
    Each chunk slides forward by (chunk_size - overlap) words to preserve
    context across chunk boundaries.

    Args:
        pages: List of per-page text strings from extract_text().
        chunk_size: Number of words per chunk. Defaults to 500.
        overlap: Number of words repeated between consecutive chunks. Defaults to 50.

    Returns:
        A list of dicts, each with:
            - text (str): The chunk's word content joined back into a string.
            - chunk_index (int): Position of this chunk across the whole document (0-based).
            - page_number (int): 1-based page number the chunk came from.
    """
    step = chunk_size - overlap
    chunks = []
    chunk_index = 0

    for page_number, page_text in enumerate(pages, start=1):
        words = page_text.split()
        if not words:
            continue

        for start in range(0, len(words), step):
            chunk_words = words[start : start + chunk_size]
            chunks.append({
                "text": " ".join(chunk_words),
                "chunk_index": chunk_index,
                "page_number": page_number,
            })
            chunk_index += 1

    return chunks
