from pydantic import BaseModel
from typing import Optional

class AgeCheckRequest(BaseModel):
    age: int
    medication: str

class AgeCheckResponse(BaseModel):
    is_safe: bool
    risk_level: str
    recommendations: Optional[list[str]] = None
    warnings: Optional[list[str]] = None
