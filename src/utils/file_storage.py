import os
from fastapi import UploadFile

BASE_UPLOAD_DIR = "/tmp/uploads"

def ensure_upload_dir():
    if not os.path.exists(BASE_UPLOAD_DIR):
        os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

def save_file(file: UploadFile) -> str:
    """
    Save an uploaded file to /tmp/uploads on Render.
    Returns the full path of the saved file.
    """
    ensure_upload_dir()

    file_path = os.path.join(BASE_UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path
