"""
Tests for dosage validation services.
"""

import pytest
from dosage_validation.dosage_calculator import DosageCalculator
from dosage_validation.range_validator import RangeValidator
from dosage_validation.renal_adjustment import RenalAdjustment


class TestDosageCalculator:
    """Test cases for DosageCalculator service."""

    @pytest.fixture
    def dosage_calculator(self):
        """Create DosageCalculator instance for testing."""
        return DosageCalculator()

    def test_calculate_dosage_adult(self, dosage_calculator):
        """Test dosage calculation for adult patient."""
        result = dosage_calculator.calculate_dosage("acetaminophen", 35, 70)

        assert result["drug_name"] == "acetaminophen"
        assert result["patient_age"] == 35
        assert result["age_category"] == "adult"
        assert "calculated_dose" in result
        assert "max_daily_dose" in result
        assert "warnings" in result

    def test_calculate_dosage_pediatric(self, dosage_calculator):
        """Test dosage calculation for pediatric patient."""
        result = dosage_calculator.calculate_dosage("amoxicillin", 8, 25)

        assert result["age_category"] == "pediatric"
        assert "calculated_dose" in result
        assert result["dosing_method"] == "weight_based"
        assert result["weight_kg"] == 25

    def test_calculate_dosage_geriatric(self, dosage_calculator):
        """Test dosage calculation for geriatric patient."""
        result = dosage_calculator.calculate_dosage("lisinopril", 75)

        assert result["age_category"] == "geriatric"
        assert "calculated_dose" in result
        assert "warnings" in result

    def test_validate_prescription_dosage(self, dosage_calculator):
        """Test prescription dosage validation."""
        result = dosage_calculator.validate_prescription_dosage("acetaminophen", "500mg", 35, 70)

        assert result["drug_name"] == "acetaminophen"
        assert result["prescribed_dose"] == "500mg"
        assert "valid" in result
        assert "warnings" in result

    def test_get_dosage_range(self, dosage_calculator):
        """Test dosage range retrieval."""
        result = dosage_calculator.get_dosage_range("ibuprofen", 35)

        assert result["drug_name"] == "ibuprofen"
        assert result["age"] == 35
        assert "acceptable_range" in result


class TestRangeValidator:
    """Test cases for RangeValidator service."""

    @pytest.fixture
    def range_validator(self):
        """Create RangeValidator instance for testing."""
        return RangeValidator()

    def test_validate_dosage_range_safe(self, range_validator):
        """Test dosage range validation for safe dose."""
        result = range_validator.validate_dosage_range("acetaminophen", 500, 35, 70)

        assert result["drug_name"] == "acetaminophen"
        assert result["prescribed_dose"] == 500
        assert result["within_range"] is True
        assert result["safety_status"] == "safe"

    def test_validate_dosage_range_excessive(self, range_validator):
        """Test dosage range validation for excessive dose."""
        result = range_validator.validate_dosage_range("acetaminophen", 5000, 35, 70)

        assert result["within_range"] is False
        assert result["safety_status"] == "unsafe"
        assert len(result["warnings"]) > 0

    def test_get_dosage_alerts(self, range_validator):
        """Test dosage alerts retrieval."""
        alerts = range_validator.get_dosage_alerts("warfarin", 10, 75, ["aspirin"])

        assert isinstance(alerts, list)
        # Should have alerts for warfarin + aspirin combination

    def test_calculate_dose_adjustment(self, range_validator):
        """Test dose adjustment calculation."""
        result = range_validator.calculate_dose_adjustment(
            "lisinopril", 10, {"min": 5, "max": 20}, {"age": 75, "creatinine_clearance": 40}
        )

        assert result["drug_name"] == "lisinopril"
        assert "recommended_dose" in result
        assert "adjustment_factor" in result


class TestRenalAdjustment:
    """Test cases for RenalAdjustment service."""

    @pytest.fixture
    def renal_adjustment(self):
        """Create RenalAdjustment instance for testing."""
        return RenalAdjustment()

    def test_calculate_renal_adjustment_normal(self, renal_adjustment):
        """Test renal adjustment for normal renal function."""
        result = renal_adjustment.calculate_renal_adjustment("amoxicillin", 90, 500)

        assert result["drug_name"] == "amoxicillin"
        assert result["renal_category"] == "normal"
        assert result["requires_adjustment"] is False

    def test_calculate_renal_adjustment_impaired(self, renal_adjustment):
        """Test renal adjustment for impaired renal function."""
        result = renal_adjustment.calculate_renal_adjustment("lisinopril", 35, 10)

        assert result["renal_category"] == "moderate"
        assert result["requires_adjustment"] is True
        assert "recommended_dose" in result
        assert "warnings" in result

    def test_estimate_creatinine_clearance(self, renal_adjustment):
        """Test creatinine clearance estimation."""
        crcl = renal_adjustment.estimate_creatinine_clearance(70, 80, 1.2, "male")

        assert isinstance(crcl, float)
        assert crcl > 0

    def test_validate_renal_dose(self, renal_adjustment):
        """Test renal dose validation."""
        result = renal_adjustment.validate_renal_dose("lisinopril", 10, 35)

        assert result["drug_name"] == "lisinopril"
        assert "valid" in result
        assert "warnings" in result

    def test_batch_renal_adjustments(self, renal_adjustment):
        """Test batch renal adjustments."""
        prescriptions = [
            {"drug_name": "amoxicillin", "creatinine_clearance": 90},
            {"drug_name": "lisinopril", "creatinine_clearance": 35}
        ]

        results = renal_adjustment.batch_renal_adjustments(prescriptions)

        assert len(results) == 2
        assert results[0]["drug_name"] == "amoxicillin"
        assert results[1]["drug_name"] == "lisinopril"
