import pathlib
import pytest
from fastapi.testclient import TestClient

from main import app

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Provide a TestClient with an isolated temporary database per test.

    Patches the DB path so tests never write to the real doctalk.db.
    Using TestClient as a context manager triggers the lifespan so
    init_db() runs before requests are made.
    """
    monkeypatch.setattr("db.database.DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:
        yield c


def test_upload_valid_pdf_returns_200_and_session_id(client):
    with open(FIXTURES_DIR / "sample.pdf", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert "session_id" in body
    assert body["filename"] == "sample.pdf"
    assert body["status"] == "ready"
    assert body["chunks"] > 0
    assert body["pages"] > 0


def test_upload_invalid_file_type_returns_400(client):
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"some plain text content", "text/plain")},
    )

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_upload_oversized_file_returns_400(client, monkeypatch):
    monkeypatch.setattr("routes.upload.MAX_UPLOAD_BYTES", 10)

    with open(FIXTURES_DIR / "sample.pdf", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 400
    assert "limit" in response.json()["detail"]


def test_history_unknown_session_returns_404(client):
    response = client.get("/history/does-not-exist")

    assert response.status_code == 404
