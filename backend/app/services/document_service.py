import os
from sqlalchemy.orm import Session
from ..models.document import Document
from ..schemas.document import DocumentCreate

class DocumentService:
    @staticmethod
    def create_document(db: Session, document: DocumentCreate):
        db_document = Document(**document.dict())
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def get_user_documents(db: Session, user_id: int):
        return db.query(Document).filter(Document.user_id == user_id).all()

    @staticmethod
    def get_document(db: Session, document_id: int):
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def delete_document(db: Session, document_id: int):
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            # Remove file from filesystem
            if os.path.exists(db_document.file_path):
                os.remove(db_document.file_path)
            db.delete(db_document)
            db.commit()
        return db_document
