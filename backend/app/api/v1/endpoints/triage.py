from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.document_service import upload_document

router = APIRouter()

@router.post("/upload")
def upload_triage_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = upload_document(db, file)
    return result
