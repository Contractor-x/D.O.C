from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SideEffectBase(BaseModel):
    medication_id: int
    name: str
    description: Optional[str] = None
    severity: Optional[str] = None
    frequency: Optional[str] = None

class SideEffectCreate(SideEffectBase):
    pass

class SideEffectUpdate(SideEffectBase):
    pass

class SideEffectResponse(SideEffectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
