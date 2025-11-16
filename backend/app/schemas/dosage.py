from pydantic import BaseModel
from typing import Optional

class DosageRequest(BaseModel):
    weight: float
    medication: str
    age: int

class DosageResponse(BaseModel):
    recommended_dosage: str
    calculation_method: str
    warnings: Optional[list[str]] = None
    adjustments: Optional[list[str]] = None
