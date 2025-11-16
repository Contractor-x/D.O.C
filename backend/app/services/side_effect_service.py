from sqlalchemy.orm import Session
from ..models.side_effect import SideEffect
from ..schemas.side_effect import SideEffectCreate

class SideEffectService:
    @staticmethod
    def get_side_effects_by_drug_id(db: Session, drug_id: int):
        return db.query(SideEffect).filter(SideEffect.medication_id == drug_id).all()

    @staticmethod
    def create_side_effect(db: Session, side_effect: SideEffectCreate):
        db_side_effect = SideEffect(**side_effect.dict())
        db.add(db_side_effect)
        db.commit()
        db.refresh(db_side_effect)
        return db_side_effect
