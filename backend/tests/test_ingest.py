import os
import pathlib
import pytest
from dotenv import load_dotenv

load_dotenv()

from services.ingest import ingest_pdf
from services.vector_store import get_client, delete_session

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"
SESSION_ID = "test-ingest-session"


@pytest.fixture(autouse=True)
def cleanup():
    """Delete the test ChromaDB collection before and after each test."""
    delete_session(SESSION_ID)
    yield
    delete_session(SESSION_ID)


def test_ingest_pdf_returns_correct_counts():
    file_bytes = (FIXTURES_DIR / "sample.pdf").read_bytes()
    result = ingest_pdf(SESSION_ID, file_bytes)

    assert result["chunks"] > 0
    assert result["pages"] > 0


def test_ingest_pdf_stores_collection_in_chromadb():
    file_bytes = (FIXTURES_DIR / "sample.pdf").read_bytes()
    ingest_pdf(SESSION_ID, file_bytes)

    client = get_client()
    collection = client.get_collection(name=SESSION_ID)
    assert collection is not None


def test_ingest_pdf_chunk_count_matches_collection():
    file_bytes = (FIXTURES_DIR / "sample.pdf").read_bytes()
    result = ingest_pdf(SESSION_ID, file_bytes)

    client = get_client()
    collection = client.get_collection(name=SESSION_ID)
    assert collection.count() == result["chunks"]
