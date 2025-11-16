from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.research_service import get_research_updates

router = APIRouter()

@router.get("/")
def read_research_updates(db: Session = Depends(get_db)):
    return get_research_updates(db)
