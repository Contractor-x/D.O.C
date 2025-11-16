import pytest
from ..app.services.dosage_service import DosageService
from ..app.schemas.dosage import DosageRequest

def test_calculate_dosage_paracetamol():
    request = DosageRequest(weight=70, medication="paracetamol", age=30)
    response = DosageService.calculate_dosage(request)

    assert "mg" in response.recommended_dosage
    assert response.calculation_method == "Standard mg/kg dosing"

def test_calculate_dosage_ibuprofen():
    request = DosageRequest(weight=60, medication="ibuprofen", age=25)
    response = DosageService.calculate_dosage(request)

    assert "mg" in response.recommended_dosage
    assert response.calculation_method == "Standard mg/kg dosing"

def test_calculate_dosage_unknown_medication():
    request = DosageRequest(weight=50, medication="unknown_drug", age=40)
    response = DosageService.calculate_dosage(request)

    assert "Consult physician" in response.recommended_dosage
    assert response.calculation_method == "Physician consultation required"

def test_dosage_with_age_warnings():
    request = DosageRequest(weight=5, medication="paracetamol", age=1)
    response = DosageService.calculate_dosage(request)

    assert response.warnings is not None
    assert len(response.warnings) > 0
