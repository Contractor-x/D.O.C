from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResearchBase(BaseModel):
    title: str
    summary: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[datetime] = None

class ResearchCreate(ResearchBase):
    pass

class ResearchUpdate(ResearchBase):
    pass

class ResearchResponse(ResearchBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
