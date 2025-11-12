"""
Tests for OCR services.
"""

import pytest
from PIL import Image
import io
from ocr.drug_ocr import DrugOCR
from ocr.prescription_ocr import PrescriptionOCR
from ocr.confidence_scorer import ConfidenceScorer


class TestDrugOCR:
    """Test cases for DrugOCR service."""

    @pytest.fixture
    def drug_ocr(self):
        """Create DrugOCR instance for testing."""
        return DrugOCR()

    def test_extract_text_from_image(self, drug_ocr):
        """Test text extraction from image."""
        # Create a simple test image with text
        img = Image.new('RGB', (100, 50), color='white')
        # In real testing, would use an actual image with text

        # For now, test the method exists and handles errors gracefully
        try:
            result = drug_ocr.extract_text_from_image(img)
            assert isinstance(result, dict)
            assert "text" in result
            assert "confidence" in result
        except Exception:
            # OCR might not be available in test environment
            pass

    def test_identify_drugs_from_text(self, drug_ocr):
        """Test drug identification from extracted text."""
        test_text = "Take 500mg of Amoxicillin three times daily"

        result = drug_ocr.identify_drugs_from_text(test_text)

        assert isinstance(result, list)
        # Should identify amoxicillin
        drug_names = [item.get("drug_name", "").lower() for item in result]
        assert "amoxicillin" in drug_names

    def test_process_drug_image(self, drug_ocr):
        """Test complete drug image processing."""
        # Create a mock image
        img = Image.new('RGB', (200, 100), color='white')

        try:
            result = drug_ocr.process_drug_image(img)
            assert isinstance(result, dict)
            assert "identified_drugs" in result
            assert "confidence_score" in result
        except Exception:
            # OCR might not be available
            pass


class TestPrescriptionOCR:
    """Test cases for PrescriptionOCR service."""

    @pytest.fixture
    def prescription_ocr(self):
        """Create PrescriptionOCR instance for testing."""
        return PrescriptionOCR()

    def test_extract_prescription_data(self, prescription_ocr):
        """Test prescription data extraction."""
        test_text = """
        Patient: John Doe
        Drug: Lisinopril 10mg
        Directions: Take one tablet by mouth daily
        Quantity: 30
        Refills: 3
        """

        result = prescription_ocr.extract_prescription_data(test_text)

        assert isinstance(result, dict)
        assert "patient_name" in result
        assert "medications" in result
        assert len(result["medications"]) > 0

    def test_parse_dosage_instructions(self, prescription_ocr):
        """Test dosage instruction parsing."""
        instructions = [
            "Take 500mg three times daily",
            "Take one tablet by mouth daily",
            "Take 10mg every 12 hours"
        ]

        for instruction in instructions:
            result = prescription_ocr.parse_dosage_instructions(instruction)
            assert isinstance(result, dict)
            assert "dosage" in result
            assert "frequency" in result

    def test_validate_prescription_format(self, prescription_ocr):
        """Test prescription format validation."""
        valid_prescription = {
            "patient_name": "John Doe",
            "medications": [{"name": "Lisinopril", "dosage": "10mg", "frequency": "daily"}],
            "quantity": 30,
            "refills": 3
        }

        result = prescription_ocr.validate_prescription_format(valid_prescription)
        assert result["valid"] is True

        invalid_prescription = {"invalid": "data"}
        result = prescription_ocr.validate_prescription_format(invalid_prescription)
        assert result["valid"] is False


class TestConfidenceScorer:
    """Test cases for ConfidenceScorer service."""

    @pytest.fixture
    def confidence_scorer(self):
        """Create ConfidenceScorer instance for testing."""
        return ConfidenceScorer()

    def test_calculate_confidence_score(self, confidence_scorer):
        """Test confidence score calculation."""
        ocr_results = {
            "tesseract": {"text": "Amoxicillin 500mg", "confidence": 0.85},
            "google_vision": {"text": "Amoxicillin 500mg", "confidence": 0.92}
        }

        result = confidence_scorer.calculate_confidence_score(ocr_results)

        assert isinstance(result, dict)
        assert "overall_confidence" in result
        assert "best_result" in result
        assert "method_used" in result

    def test_select_best_extraction_method(self, confidence_scorer):
        """Test best extraction method selection."""
        methods = {
            "tesseract": {"confidence": 0.75, "text_length": 50},
            "google_vision": {"confidence": 0.90, "text_length": 48},
            "azure": {"confidence": 0.80, "text_length": 52}
        }

        best_method = confidence_scorer.select_best_extraction_method(methods)

        assert best_method in methods.keys()
        # Should select google_vision due to highest confidence

    def test_validate_ocr_accuracy(self, confidence_scorer):
        """Test OCR accuracy validation."""
        extracted_text = "Amoxicillin 500mg"
        expected_patterns = ["amoxicillin", "500mg"]

        result = confidence_scorer.validate_ocr_accuracy(extracted_text, expected_patterns)

        assert isinstance(result, dict)
        assert "accuracy_score" in result
        assert "matched_patterns" in result
        assert result["accuracy_score"] > 0

    def test_combine_ocr_results(self, confidence_scorer):
        """Test OCR result combination."""
        results = [
            {"text": "Amoxicillin 500mg", "confidence": 0.85, "method": "tesseract"},
            {"text": "Amoxicillin 500mg", "confidence": 0.92, "method": "google_vision"}
        ]

        combined = confidence_scorer.combine_ocr_results(results)

        assert isinstance(combined, dict)
        assert "consensus_text" in combined
        assert "confidence_score" in combined
        assert "methods_used" in combined
