from fastapi import APIRouter, Depends
from ...services.age_service import verify_age

router = APIRouter()

@router.post("/verify")
def verify_patient_age(age: int, medication: str):
    result = verify_age(age, medication)
    return result
