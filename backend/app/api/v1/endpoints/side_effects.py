from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.side_effect_service import get_side_effects

router = APIRouter()

@router.get("/")
def read_side_effects(drug_id: int, db: Session = Depends(get_db)):
    return get_side_effects(db, drug_id)
