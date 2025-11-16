from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedicationBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    description: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    ndc_code: Optional[str] = None

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(MedicationBase):
    pass

class MedicationResponse(MedicationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
