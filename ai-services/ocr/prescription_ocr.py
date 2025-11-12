"""
Prescription OCR Service
Handles optical character recognition for prescription documents.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from .preprocessing import ImagePreprocessor
from .confidence_scorer import ConfidenceScorer

logger = logging.getLogger(__name__)


class PrescriptionOCR:
    """OCR service for prescription document analysis."""

    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.confidence_scorer = ConfidenceScorer()

        # Prescription-specific patterns
        self.prescription_patterns = {
            'dea_number': r'DEA\s*#?\s*[A-Z]{2}\d{7}',
            'npi_number': r'NPI\s*#?\s*\d{10}',
            'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'quantity': r'(?:Qty|Quantity)\s*:\s*\d+',
            'refills': r'(?:Refills?)\s*:\s*\d+',
            'directions': r'(?:Sig|Directions?)\s*:\s*[A-Za-z\s]+',
            'patient_name': r'Patient\s*:\s*[A-Z][a-z]+\s+[A-Z][a-z]+',
            'doctor_name': r'(?:Dr\.|Doctor)\s*[A-Z][a-z]+\s+[A-Z][a-z]+',
        }

    async def extract_prescription_data(self, image_path: str) -> Dict:
        """
        Extract structured data from prescription image.

        Args:
            image_path: Path to prescription image

        Returns:
            Dict containing extracted prescription data
        """
        try:
            # Read and preprocess image
            image = Image.open(image_path)
            processed_image = self.preprocessor.preprocess_for_ocr(image)

            # Extract text using OCR
            ocr_result = self._perform_ocr(processed_image)

            if not ocr_result["success"]:
                return ocr_result

            text = ocr_result["text"]

            # Extract structured prescription data
            prescription_data = self._parse_prescription_text(text)

            return {
                "success": True,
                "data": prescription_data,
                "confidence": ocr_result["confidence"],
                "raw_text": text
            }

        except Exception as e:
            logger.error(f"Prescription OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {},
                "confidence": 0.0
            }

    def _perform_ocr(self, image: Image.Image) -> Dict:
        """Perform OCR on prescription image."""
        try:
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Import pytesseract here to avoid import errors if not installed
            import pytesseract

            # Get OCR data with confidence scores
            data = pytesseract.image_to_data(opencv_image, output_type=pytesseract.Output.DICT)

            # Extract text and calculate average confidence
            text_parts = []
            confidences = []

            for i, confidence in enumerate(data['conf']):
                if int(confidence) > 60:  # Filter low confidence
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(confidence))

            extracted_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                "success": True,
                "text": extracted_text,
                "confidence": avg_confidence / 100.0,
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }

    def _parse_prescription_text(self, text: str) -> Dict:
        """
        Parse prescription text to extract structured data.

        Args:
            text: Raw OCR text from prescription

        Returns:
            Dict with parsed prescription data
        """
        prescription_data = {
            "drug_name": None,
            "dosage": None,
            "quantity": None,
            "refills": None,
            "directions": None,
            "patient_name": None,
            "doctor_name": None,
            "dea_number": None,
            "npi_number": None,
            "date": None,
            "parsed_fields": []
        }

        # Extract drug name (usually the most prominent capitalized text)
        prescription_data["drug_name"] = self._extract_drug_name(text)
        if prescription_data["drug_name"]:
            prescription_data["parsed_fields"].append("drug_name")

        # Extract dosage
        prescription_data["dosage"] = self._extract_dosage(text)
        if prescription_data["dosage"]:
            prescription_data["parsed_fields"].append("dosage")

        # Extract using regex patterns
        for field, pattern in self.prescription_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group().strip()
                prescription_data[field] = self._clean_extracted_value(value, field)
                prescription_data["parsed_fields"].append(field)

        return prescription_data

    def _extract_drug_name(self, text: str) -> Optional[str]:
        """Extract drug name from prescription text."""
        # Look for capitalized words that are likely drug names
        words = text.split()
        potential_drugs = []

        for word in words:
            # Drug names are typically capitalized and not common words
            if (len(word) > 3 and
                word[0].isupper() and
                not word.lower() in ['patient', 'doctor', 'directions', 'quantity', 'refills']):
                potential_drugs.append(word)

        if potential_drugs:
            # Return the first 1-3 capitalized words as drug name
            return ' '.join(potential_drugs[:3])

        return None

    def _extract_dosage(self, text: str) -> Optional[str]:
        """Extract dosage information from prescription text."""
        # Look for dosage patterns
        dosage_patterns = [
            r'\d+\s*mg\s*(?:daily|twice|times?\s*per\s*day|q\.?d\.?|b\.?i\.?d\.?)',
            r'\d+\s*ml\s*(?:daily|twice|times?\s*per\s*day)',
            r'\d+\s*(?:tablet|capsule|pill)s?\s*(?:daily|twice|times?\s*per\s*day)',
            r'\d+\s*units?\s*(?:daily|twice|times?\s*per\s*day)',
        ]

        for pattern in dosage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()

        # Fallback: look for any dosage-like pattern
        simple_dosage = re.search(r'\d+\s*(mg|ml|tablet|capsule|pill|unit)s?', text, re.IGNORECASE)
        if simple_dosage:
            return simple_dosage.group().strip()

        return None

    def _clean_extracted_value(self, value: str, field: str) -> str:
        """Clean extracted values based on field type."""
        if field in ['quantity', 'refills']:
            # Extract just the number
            number_match = re.search(r'\d+', value)
            return number_match.group() if number_match else value

        elif field == 'date':
            # Try to parse and standardize date
            return self._standardize_date(value)

        elif field in ['patient_name', 'doctor_name']:
            # Clean up name formatting
            return value.replace('Patient:', '').replace('Dr.:', '').replace('Doctor:', '').strip()

        return value

    def _standardize_date(self, date_str: str) -> str:
        """Standardize date format."""
        try:
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.strftime('%Y-%m-%d')
                except ValueError:
                    continue

            # If no format matches, return original
            return date_str

        except Exception:
            return date_str

    def validate_prescription(self, prescription_data: Dict) -> Dict:
        """
        Validate extracted prescription data for completeness and accuracy.

        Args:
            prescription_data: Parsed prescription data

        Returns:
            Validation results
        """
        validation = {
            "is_valid": False,
            "completeness_score": 0.0,
            "issues": [],
            "recommendations": []
        }

        required_fields = ['drug_name', 'dosage', 'quantity', 'directions']
        parsed_fields = prescription_data.get('parsed_fields', [])

        # Check required fields
        missing_fields = [field for field in required_fields if field not in parsed_fields]
        if missing_fields:
            validation["issues"].extend([f"Missing {field}" for field in missing_fields])

        # Calculate completeness score
        total_fields = len(self.prescription_patterns) + 2  # +2 for drug_name and dosage
        validation["completeness_score"] = len(parsed_fields) / total_fields

        # Validate specific fields
        if prescription_data.get('quantity'):
            try:
                qty = int(prescription_data['quantity'])
                if qty <= 0 or qty > 1000:
                    validation["issues"].append("Unusual quantity value")
            except ValueError:
                validation["issues"].append("Invalid quantity format")

        if prescription_data.get('refills'):
            try:
                refills = int(prescription_data['refills'])
                if refills < 0 or refills > 12:
                    validation["issues"].append("Unusual refills value")
            except ValueError:
                validation["issues"].append("Invalid refills format")

        # Determine overall validity
        validation["is_valid"] = (
            'drug_name' in parsed_fields and
            'dosage' in parsed_fields and
            len(validation["issues"]) == 0
        )

        # Generate recommendations
        if not validation["is_valid"]:
            validation["recommendations"].append("Consider re-scanning the prescription")
            if validation["completeness_score"] < 0.5:
                validation["recommendations"].append("Prescription image may be of poor quality")

        return validation
