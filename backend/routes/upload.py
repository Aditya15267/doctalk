import os
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile

from db.session_store import create_session
from models.schemas import UploadResponse
from services.ingest import ingest_pdf

router = APIRouter()

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB")) * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile):
    """
    Accept a PDF upload, run the ingest pipeline, and persist the session.

    Validates that the file is a PDF and within the size limit before
    processing. Runs the full extract → chunk → embed → store pipeline
    and saves the session metadata to SQLite.

    Args:
        file: The uploaded file from the multipart/form-data request.

    Returns:
        UploadResponse with session_id, filename, pages, chunks, and status.

    Raises:
        HTTPException 400: If the file is not a PDF or exceeds the size limit.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {os.getenv('MAX_UPLOAD_SIZE_MB')}MB limit.",
        )

    session_id = str(uuid4())

    result = ingest_pdf(session_id, file_bytes)

    await create_session(
        session_id=session_id,
        filename=file.filename,
        pages=result["pages"],
        chunk_count=result["chunks"],
    )

    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        pages=result["pages"],
        chunks=result["chunks"],
        status="ready",
    )
