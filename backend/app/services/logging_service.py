dy hfrom sqlalchemy.orm import Session
from ..models.patient_log import PatientLog
from ..schemas.log import LogCreate

class LoggingService:
    @staticmethod
    def create_log(db: Session, log: LogCreate):
        db_log = PatientLog(**log.dict())
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def get_user_logs(db: Session, user_id: int):
        return db.query(PatientLog).filter(PatientLog.user_id == user_id).order_by(PatientLog.created_at.desc()).all()

    @staticmethod
    def get_log_by_id(db: Session, log_id: int):
        return db.query(PatientLog).filter(PatientLog.id == log_id).first()

    @staticmethod
    def mark_sent_to_doctor(db: Session, log_id: int):
        db_log = db.query(PatientLog).filter(PatientLog.id == log_id).first()
        if db_log:
            db_log.sent_to_doctor = True
            db.commit()
            db.refresh(db_log)
        return db_log
