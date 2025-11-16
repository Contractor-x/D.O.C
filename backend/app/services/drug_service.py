from sqlalchemy.orm import Session
from ..models.medication import Medication
from ..schemas.medication import MedicationCreate, MedicationUpdate

class DrugService:
    @staticmethod
    def get_drug_by_name(db: Session, name: str):
        return db.query(Medication).filter(Medication.name.ilike(f"%{name}%")).first()

    @staticmethod
    def create_drug(db: Session, drug: MedicationCreate):
        db_drug = Medication(**drug.dict())
        db.add(db_drug)
        db.commit()
        db.refresh(db_drug)
        return db_drug

    @staticmethod
    def update_drug(db: Session, drug_id: int, drug_update: MedicationUpdate):
        db_drug = db.query(Medication).filter(Medication.id == drug_id).first()
        if db_drug:
            update_data = drug_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_drug, field, value)
            db.commit()
            db.refresh(db_drug)
        return db_drug
