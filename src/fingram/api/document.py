from fastapi import APIRouter, UploadFile,File ,HTTPException

import logging

logger = logging.getLogger(__name__) 

file_router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024
FILE_FORMAT = "PDF"


@file_router.post("/")
async def upload_pdf_file(file: UploadFile = File(...)):
    """Accept an uploaded PDF, validate its size and file signature, and confirm success. """

    filename = file.filename
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        logger.warning("Upload rejected: %s is %d bytes (limit %d)", filename, len(content), MAX_FILE_SIZE)
        raise HTTPException(status_code=413, detail="File must be 20 MB or smaller")

    if not content.startswith(b"%PDF-"):
        logger.warning(" Upload recjected: %s is not a valid %s format", filename, FILE_FORMAT)
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

    return {"status": "success", "filename": file.filename}

    