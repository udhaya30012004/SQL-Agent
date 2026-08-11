"""
Pandas Agent Utility Router

Provides a file-upload endpoint for CSV datasets.
All endpoints require authentication.
"""

import os
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from api.app.core.security import get_current_user
from api.app.models.user import User

router = APIRouter(prefix="/pandas", tags=["Pandas Agent Utilities"])

# Folder to store uploaded CSV datasets on the server
UPLOAD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_csv_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a CSV sheet to the backend storage.
    Returns the path to be used when creating / running a chat session.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV files are supported.",
        )

    # Ensure uploads directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save file to server
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file.filename,
            "file_path": file_path,
            "status": "success",
            "message": "CSV dataset uploaded successfully.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file to disk: {str(e)}",
        )
