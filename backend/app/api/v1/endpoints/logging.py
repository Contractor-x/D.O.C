from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.logging_service import create_log

router = APIRouter()

@router.post("/")
def create_patient_log(log_data: dict, db: Session = Depends(get_db)):
    result = create_log(db, log_data)
    return result
