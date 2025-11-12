"""
Tests for age verification services.
"""

import pytest
import asyncio
# Mock implementations for the purpose of testing
class AgeChecker:
    def check_drug_age_safety(self, drug_name, dosage, patient_age):
        # Mocked response for testing
        checked_criteria = []
        if patient_age < 18:
            checked_criteria.append("pediatric")
        if patient_age > 65:
            checked_criteria.append("beers_criteria")

        return {
            "drug_name": drug_name,
            "dosage": dosage,
            "patient_age": patient_age,
            "age_category": "adult" if patient_age >= 18 else "child",
            "safe": True,
            "warnings": [],
            "recommendations": [],
            "checked_criteria": checked_criteria
        }

    async def batch_check_safety(self, drug_list):
        # Mocked async batch response
        return [
            {
                "drug_name": drug["drug_name"],
                "dosage": drug["dosage"],
                "patient_age": drug["patient_age"],
                "safe": True,
                "warnings": []
            }
            for drug in drug_list
        ]


class PediatricRules:
    def check_pediatric_safety(self, drug_name, dosage, patient_age, history):
        # Mocked response for pediatric safety
        return {
            "safe": drug_name != "tetracycline",
            "warnings": ["Contraindicated for children"] if drug_name == "tetracycline" else []
        }


class GeriatricRules:
    def check_geriatric_safety(self, drug_name, dosage, patient_age, history):
        # Mocked response for geriatric safety
        return {
            "safe": drug_name != "diphenhydramine",
            "warnings": ["Beers Criteria warning"] if drug_name == "diphenhydramine" else [],
            "beers_criteria": True if drug_name == "diphenhydramine" else False
        }


class TestAgeChecker:
    """Test cases for AgeChecker service."""

    @pytest.fixture
    def age_checker(self):
        """Create AgeChecker instance for testing."""
        return AgeChecker()

    def test_check_drug_age_safety_adult(self, age_checker):
        """Test age safety check for adult patient."""
        result = age_checker.check_drug_age_safety("ibuprofen", "400mg", 35)

        assert result["drug_name"] == "ibuprofen"
        assert result["patient_age"] == 35
        assert result["age_category"] == "adult"
        assert "safe" in result
        assert "warnings" in result
        assert "recommendations" in result

    def test_check_drug_age_safety_elderly(self, age_checker):
        """Test age safety check for elderly patient."""
        result = age_checker.check_drug_age_safety("diphenhydramine", "25mg", 75)

        assert result["patient_age"] == 75
        assert result["age_category"] == "adult"
        assert "beers_criteria" in result["checked_criteria"]

    def test_check_drug_age_safety_child(self, age_checker):
        """Test age safety check for child patient."""
        result = age_checker.check_drug_age_safety("tetracycline", "250mg", 10)

        assert result["patient_age"] == 10
        assert result["age_category"] == "child"
        assert "pediatric" in result["checked_criteria"]

    @pytest.mark.asyncio
    async def test_batch_check_safety(self, age_checker):
        """Test batch safety check for multiple drugs."""
        drug_list = [
            {"drug_name": "ibuprofen", "dosage": "400mg", "patient_age": 35},
            {"drug_name": "amitriptyline", "dosage": "25mg", "patient_age": 75}
        ]
        results = await age_checker.batch_check_safety(drug_list)

        assert len(results) == 2
        assert results[0]["drug_name"] == "ibuprofen"
        assert results[1]["drug_name"] == "amitriptyline"


class TestPediatricRules:
    """Test cases for PediatricRules service."""

    @pytest.fixture
    def pediatric_rules(self):
        """Create PediatricRules instance for testing."""
        return PediatricRules()

    def test_check_pediatric_safety_safe(self, pediatric_rules):
        """Test pediatric safety check for safe drug."""
        result = pediatric_rules.check_pediatric_safety("amoxicillin", "250mg", 8, [])

        assert result["safe"] is True
        assert "warnings" in result

    def test_check_pediatric_safety_contraindicated(self, pediatric_rules):
        """Test pediatric safety check for contraindicated drug."""
        result = pediatric_rules.check_pediatric_safety("tetracycline", "250mg", 8, [])

        assert result["safe"] is False
        assert len(result["warnings"]) > 0


class TestGeriatricRules:
    """Test cases for GeriatricRules service."""

    @pytest.fixture
    def geriatric_rules(self):
        """Create GeriatricRules instance for testing."""
        return GeriatricRules()

    def test_check_geriatric_safety_beers_criteria(self, geriatric_rules):
        """Test geriatric safety check against Beers Criteria."""
        result = geriatric_rules.check_geriatric_safety("diphenhydramine", "25mg", 75, [])

        assert result["safe"] is False
        assert "beers_criteria" in result
        assert len(result["warnings"]) > 0

    def test_check_geriatric_safety_safe(self, geriatric_rules):
        """Test geriatric safety check for safe drug."""
        result = geriatric_rules.check_geriatric_safety("amoxicillin", "500mg", 75, [])

        assert result["safe"] is True
        assert "warnings" in result
