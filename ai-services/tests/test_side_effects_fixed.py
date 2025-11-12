"""
Tests for side effects services.
"""

import pytest
from typing import Dict
from side_effects.side_effect_extractor import SideEffectExtractor
from side_effects.severity_classifier import SeverityClassifier
from side_effects.interaction_checker import InteractionChecker


class TestSideEffectExtractor:
    """Test cases for SideEffectExtractor service."""

    @pytest.fixture
    def side_effect_extractor(self):
        """Create SideEffectExtractor instance for testing."""
        return SideEffectExtractor()

    def test_extract_side_effects_known_drug(self, side_effect_extractor):
        """Test side effect extraction for known drug."""
        result = side_effect_extractor.extract_side_effects("ibuprofen", 35)

        assert result["drug_name"] == "ibuprofen"
        assert "common_side_effects" in result
        assert "rare_side_effects" in result
        assert "severity_distribution" in result
        assert "recommendations" in result

    def test_extract_side_effects_with_age(self, side_effect_extractor):
        """Test side effect extraction with age considerations."""
        result = side_effect_extractor.extract_side_effects("ibuprofen", 75)

        assert result["drug_name"] == "ibuprofen"
        assert "age_related_effects" in result
        assert len(result["age_related_effects"]) > 0

    def test_extract_side_effects_with_conditions(self, side_effect_extractor):
        """Test side effect extraction with patient conditions."""
        result = side_effect_extractor.extract_side_effects("ibuprofen", 50, ["heart failure"])

        assert result["drug_name"] == "ibuprofen"
        assert "condition_related_effects" in result
        assert len(result["condition_related_effects"]) > 0

    def test_predict_side_effect_risk(self, side_effect_extractor):
        """Test side effect risk prediction."""
        patient_profile = {
            "age": 75,
            "weight_kg": 65,
            "conditions": ["heart failure"],
            "gender": "female"
        }

        result = side_effect_extractor.predict_side_effect_risk("ibuprofen", patient_profile)

        assert result["drug_name"] == "ibuprofen"
        assert "predicted_risk" in result
        assert "risk_score" in result
        assert "risk_factors" in result

    def test_analyze_side_effect_text(self, side_effect_extractor):
        """Test side effect text analysis."""
        text = "Patient experienced nausea, vomiting, and severe headache after taking the medication."

        result = side_effect_extractor.analyze_side_effect_text(text)

        assert "found_side_effects" in result
        assert "severity_assessment" in result
        assert result["total_mentions"] > 0


class TestSeverityClassifier:
    """Test cases for SeverityClassifier service."""

    @pytest.fixture
    def severity_classifier(self):
        """Create SeverityClassifier instance for testing."""
        return SeverityClassifier()

    def test_classify_severity_mild(self, severity_classifier):
        """Test severity classification for mild side effect."""
        result = severity_classifier.classify_severity("headache")

        assert result["side_effect"] == "headache"
        assert result["severity_level"] == "mild"
        assert result["severity_score"] <= 2
        assert "requires_attention" in result

    def test_classify_severity_severe(self, severity_classifier):
        """Test severity classification for severe side effect."""
        result = severity_classifier.classify_severity("anaphylaxis")

        assert result["side_effect"] == "anaphylaxis"
        assert result["severity_level"] == "life_threatening"
        assert result["severity_score"] >= 4
        assert result["requires_attention"] is True

    def test_classify_severity_with_context(self, severity_classifier):
        """Test severity classification with patient context."""
        context = {"age": 75, "conditions": ["diabetes"]}
        result = severity_classifier.classify_severity("hypoglycemia", context)

        assert result["side_effect"] == "hypoglycemia"
        assert result["severity_level"] == "severe"

    def test_batch_classify_severity(self, severity_classifier):
        """Test batch severity classification."""
        side_effects = ["nausea", "anaphylaxis", "headache"]
        results = severity_classifier.batch_classify_severity(side_effects)

        assert len(results) == 3
        assert results[0]["side_effect"] == "nausea"
        assert results[1]["side_effect"] == "anaphylaxis"


class TestInteractionChecker:
    """Test cases for InteractionChecker service."""

    @pytest.fixture
    def interaction_checker(self):
        """Create InteractionChecker instance for testing."""
        return InteractionChecker()

    def test_check_drug_interactions_no_interactions(self, interaction_checker):
        """Test drug interaction check with no interactions."""
        result = interaction_checker.check_drug_interactions(["amoxicillin", "acetaminophen"])

        assert result["total_interactions"] == 0
        assert result["requires_attention"] is False
        assert len(result["drug_drug_interactions"]) == 0

    def test_check_drug_interactions_with_interactions(self, interaction_checker):
        """Test drug interaction check with known interactions."""
        result = interaction_checker.check_drug_interactions(["warfarin", "aspirin"])

        assert result["total_interactions"] > 0
        assert result["requires_attention"] is True
        assert len(result["drug_drug_interactions"]) > 0
        assert "recommendations" in result

    def test_check_drug_disease_interactions(self, interaction_checker):
        """Test drug-disease interaction check."""
        result = interaction_checker.check_drug_interactions(["ibuprofen"], ["heart failure"])

        assert result["total_interactions"] > 0
        assert len(result["drug_disease_interactions"]) > 0

    def test_get_interaction_details(self, interaction_checker):
        """Test detailed interaction information retrieval."""
        result = interaction_checker.get_interaction_details("warfarin", "aspirin")

        assert result["drug1"] in ["warfarin", "aspirin"]
        assert result["drug2"] in ["warfarin", "aspirin"]
        assert "severity" in result
        assert "effect" in result

    def test_check_contraindications(self, interaction_checker):
        """Test contraindication checking."""
        patient_profile = {
            "allergies": ["penicillin"],
            "conditions": ["asthma"]
        }

        result = interaction_checker.check_contraindications("amoxicillin", patient_profile)

        assert result["drug"] == "amoxicillin"
        assert result["safe_to_use"] is False
        assert len(result["contraindications"]) > 0

    def test_get_alternative_medications(self, interaction_checker):
        """Test alternative medication suggestions."""
        alternatives = interaction_checker.get_alternative_medications("warfarin", "aspirin")

        assert isinstance(alternatives, list)
        assert len(alternatives) > 0
        assert "alternative" in alternatives[0]
        assert "reason" in alternatives[0]
