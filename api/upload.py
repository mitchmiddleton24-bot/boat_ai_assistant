from fastapi import APIRouter, UploadFile, File
from utils.file_storage import save_uploaded_file

router = APIRouter()

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    path = save_uploaded_file(file)
    return {"message": "File uploaded successfully", "path": path}
