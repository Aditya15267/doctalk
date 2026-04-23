import pytest
from db.database import init_db
from db.session_store import create_session, get_session
from db.message_store import save_message, save_citations, get_history


@pytest.fixture(autouse=True)
async def setup_db(tmp_path, monkeypatch):
    """
    Point the database at a fresh temporary file for each test.

    Uses pytest's tmp_path to create an isolated DB per test so tests
    never share state or pollute the real doctalk.db file.
    """
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("db.database.DB_PATH", db_path)
    await init_db()


async def test_create_and_get_session():
    await create_session(
        session_id="sess-001",
        filename="sample.pdf",
        pages=5,
        chunk_count=12,
    )

    session = await get_session("sess-001")

    assert session is not None
    assert session["session_id"] == "sess-001"
    assert session["filename"] == "sample.pdf"
    assert session["pages"] == 5
    assert session["chunk_count"] == 12
    assert session["status"] == "ready"


async def test_get_session_returns_none_for_unknown_id():
    result = await get_session("does-not-exist")
    assert result is None


async def test_save_message_returns_message_id():
    await create_session("sess-002", "doc.pdf", 3, 6)

    message_id = await save_message("sess-002", "user", "What is this about?")

    assert isinstance(message_id, int)
    assert message_id > 0


async def test_save_message_and_citations_appear_in_history():
    await create_session("sess-003", "doc.pdf", 3, 6)

    await save_message("sess-003", "user", "What is this about?")

    assistant_id = await save_message("sess-003", "assistant", "This document covers...")
    await save_citations(assistant_id, [
        {"text": "relevant chunk text", "page_number": 2, "chunk_index": 4, "score": 1.3},
    ])

    history = await get_history("sess-003")

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["citations"] == []
    assert history[1]["role"] == "assistant"
    assert len(history[1]["citations"]) == 1
    assert history[1]["citations"][0]["page_number"] == 2
    assert history[1]["citations"][0]["chunk_text"] == "relevant chunk text"
