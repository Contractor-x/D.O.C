import pytest
from ..app.services.age_service import AgeService
from ..app.schemas.age_check import AgeCheckRequest

def test_verify_age_safe():
    request = AgeCheckRequest(age=25, medication="paracetamol", weight=70)
    response = AgeService.verify_age_safety(request)

    assert response.is_safe is True
    assert response.risk_level == "Low"

def test_verify_age_geriatric():
    request = AgeCheckRequest(age=75, medication="ibuprofen", weight=65)
    response = AgeService.verify_age_safety(request)

    assert response.is_safe is True
    assert response.risk_level == "Medium"

def test_verify_age_pediatric():
    request = AgeCheckRequest(age=5, medication="aspirin", weight=20)
    response = AgeService.verify_age_safety(request)

    assert response.is_safe is False
    assert response.risk_level == "High"
    assert len(response.warnings) > 0

def test_verify_age_unknown_medication():
    request = AgeCheckRequest(age=30, medication="unknown_drug", weight=70)
    response = AgeService.verify_age_safety(request)

    assert response.is_safe is False
    assert "Unknown medication" in response.recommendations[0]
