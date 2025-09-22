# backend/app/routes/datasets.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from ..auth import get_current_user
from ..db import db
from pathlib import Path
import uuid, shutil


router = APIRouter(prefix="/datasets", tags=["datasets"])
UPLOAD_DIR = Path.cwd() / "data" / "raw"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", dependencies=[Depends(get_current_user)])
async def upload_dataset(
    file: UploadFile = File(...), current_user=Depends(get_current_user)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")
    uid = uuid.uuid4().hex[:8]
    saved_name = f"{Path(file.filename).stem}_{uid}.csv"
    saved_path = UPLOAD_DIR / saved_name
    with saved_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    # Insert upload record in MongoDB
    upload_doc = {
        "uploader_id": str(current_user.id),
        "filename": str(saved_name),
        "original_name": file.filename,
        "status": "uploaded",
    }
    result = await db.uploads.insert_one(upload_doc)
    # Create notification in MongoDB
    notif_doc = {
        "title": "New dataset uploaded",
        "message": f"{current_user.username} uploaded {file.filename}",
        "payload": {"upload_id": str(result.inserted_id), "filename": saved_name},
        "is_read": False,
    }
    await db.notifications.insert_one(notif_doc)
    return {"upload_id": str(result.inserted_id), "filename": saved_name}
