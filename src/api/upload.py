from fastapi import APIRouter, UploadFile, File, HTTPException
from src.utils.file_storage import save_file

router = APIRouter()

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to local storage.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    saved_path = await save_file(file)
    return {"status": "success", "path": saved_path}
