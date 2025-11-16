from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LogBase(BaseModel):
    log_type: str
    content: Optional[str] = None
    transcribed_text: Optional[str] = None
    sent_to_doctor: bool = False

class LogCreate(LogBase):
    user_id: int

class LogUpdate(LogBase):
    pass

class LogResponse(LogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
