from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.medication import MedicationResponse
from ...services.drug_service import get_drug_by_name

router = APIRouter()

@router.get("/{drug_name}", response_model=MedicationResponse)
def read_drug(drug_name: str, db: Session = Depends(get_db)):
    drug = get_drug_by_name(db, drug_name)
    if drug is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug
