from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    file_path: str
    file_type: Optional[str] = None
    content: Optional[str] = None

class DocumentCreate(DocumentBase):
    user_id: int

class DocumentUpdate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
