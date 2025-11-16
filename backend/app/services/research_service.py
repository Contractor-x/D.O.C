from sqlalchemy.orm import Session
from ..models.research import Research
from ..schemas.research import ResearchCreate

class ResearchService:
    @staticmethod
    def get_recent_research(db: Session, limit: int = 10):
        return db.query(Research).order_by(Research.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_research(db: Session, research: ResearchCreate):
        db_research = Research(**research.dict())
        db.add(db_research)
        db.commit()
        db.refresh(db_research)
        return db_research

    @staticmethod
    def get_research_by_id(db: Session, research_id: int):
        return db.query(Research).filter(Research.id == research_id).first()
