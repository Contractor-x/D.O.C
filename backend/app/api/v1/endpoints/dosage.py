from fastapi import APIRouter, Depends
from ...services.dosage_service import calculate_dosage

router = APIRouter()

@router.post("/calculate")
def calculate_patient_dosage(weight: float, medication: str, age: int):
    result = calculate_dosage(weight, medication, age)
    return result
