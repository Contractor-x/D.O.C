import pytest
from ..app.services.drug_service import DrugService
from ..app.schemas.medication import MedicationCreate

def test_create_drug(db):
    drug_data = MedicationCreate(
        name="Aspirin",
        generic_name="Acetylsalicylic acid",
        description="Pain reliever and fever reducer"
    )
    drug = DrugService.create_drug(db, drug_data)
    assert drug.name == "Aspirin"
    assert drug.generic_name == "Acetylsalicylic acid"

def test_get_drug_by_name(db):
    # Create drug first
    drug_data = MedicationCreate(name="Ibuprofen")
    DrugService.create_drug(db, drug_data)

    # Test retrieval
    drug = DrugService.get_drug_by_name(db, "Ibuprofen")
    assert drug is not None
    assert drug.name == "Ibuprofen"

def test_get_drug_by_partial_name(db):
    # Create drug
    drug_data = MedicationCreate(name="Paracetamol")
    DrugService.create_drug(db, drug_data)

    # Test partial match
    drug = DrugService.get_drug_by_name(db, "para")
    assert drug is not None
    assert drug.name == "Paracetamol"
