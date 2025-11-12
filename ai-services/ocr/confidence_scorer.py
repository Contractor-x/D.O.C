"""
Confidence Scoring for OCR Results
Evaluates and scores OCR extraction quality.
"""

import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Scores confidence of OCR results and selects best extraction method."""

    def __init__(self):
        # Patterns for common drug-related text
        self.drug_patterns = [
            r'\b\d+\s*mg\b',  # Dosage like "10mg"
            r'\b\d+\s*ml\b',  # Volume like "5ml"
            r'\b\d{4,5}-\d{3,4}-\d{1,2}\b',  # NDC codes
            r'\b[A-Z][a-z]+\b',  # Capitalized words (drug names)
            r'\b\d+\s*(tablet|capsule|pill)s?\b',  # Formulation
        ]

        # Common drug name keywords
        self.drug_keywords = {
            'hydrochlorothiazide', 'lisinopril', 'metformin', 'simvastatin',
            'omeprazole', 'amoxicillin', 'azithromycin', 'prednisone',
            'warfarin', 'digoxin', 'furosemide', 'spironolactone',
            'metoprolol', 'atenolol', 'amlodipine', 'losartan'
        }

    def score_ocr_results(self, results: List[Dict[str, Any]]) -> List[float]:
        """
        Score multiple OCR results and return confidence scores.

        Args:
            results: List of OCR result dictionaries

        Returns:
            List of confidence scores (0-1 scale)
        """
        scores = []

        for result in results:
            if not result or not result.get("text", "").strip():
                scores.append(0.0)
                continue

            text = result["text"]
            base_confidence = result.get("confidence", 0.5)

            # Calculate content quality score
            content_score = self._calculate_content_score(text)

            # Calculate text quality score
            text_score = self._calculate_text_quality_score(text)

            # Combine scores with base confidence
            final_score = (base_confidence * 0.4) + (content_score * 0.4) + (text_score * 0.2)
            final_score = min(max(final_score, 0.0), 1.0)  # Clamp to 0-1

            scores.append(final_score)

        return scores

    def _calculate_content_score(self, text: str) -> float:
        """
        Calculate score based on presence of drug-related content.

        Args:
            text: Extracted text

        Returns:
            Content quality score (0-1)
        """
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Check for drug name matches
        drug_name_matches = sum(1 for drug in self.drug_keywords if drug in text_lower)
        if drug_name_matches > 0:
            score += min(drug_name_matches * 0.2, 0.4)  # Max 0.4 for drug names

        # Check for pattern matches
        pattern_matches = 0
        for pattern in self.drug_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1

        if pattern_matches > 0:
            score += min(pattern_matches * 0.15, 0.4)  # Max 0.4 for patterns

        # Length bonus (reasonable text length)
        word_count = len(text.split())
        if 5 <= word_count <= 100:
            score += 0.2
        elif word_count > 100:
            score += 0.1  # Some bonus for long text, but not too much

        return min(score, 1.0)

    def _calculate_text_quality_score(self, text: str) -> float:
        """
        Calculate score based on text quality indicators.

        Args:
            text: Extracted text

        Returns:
            Text quality score (0-1)
        """
        if not text:
            return 0.0

        score = 0.0

        # Check for proper capitalization (drug names are often capitalized)
        words = text.split()
        capitalized_words = sum(1 for word in words if len(word) > 1 and word[0].isupper())
        if words:
            cap_ratio = capitalized_words / len(words)
            if 0.1 <= cap_ratio <= 0.8:  # Reasonable capitalization
                score += 0.3

        # Check for numbers (dosages, NDC codes)
        number_count = len(re.findall(r'\d', text))
        if number_count > 0:
            score += min(number_count * 0.05, 0.3)  # Max 0.3 for numbers

        # Check for special characters (should be minimal in drug text)
        special_chars = len(re.findall(r'[^\w\s-]', text))
        if special_chars < len(text) * 0.1:  # Less than 10% special chars
            score += 0.2

        # Check for common OCR errors (repeated characters, gibberish)
        if not self._has_ocr_artifacts(text):
            score += 0.2

        return min(score, 1.0)

    def _has_ocr_artifacts(self, text: str) -> bool:
        """
        Check for common OCR artifacts that indicate poor quality.

        Args:
            text: Text to check

        Returns:
            True if artifacts detected
        """
        # Check for excessive repeated characters
        if re.search(r'(.)\1{4,}', text):  # 5+ repeated chars
            return True

        # Check for gibberish patterns
        words = text.split()
        gibberish_words = 0

        for word in words:
            # Words with no vowels or excessive consonants
            if len(word) > 3 and not re.search(r'[aeiouAEIOU]', word):
                gibberish_words += 1
            # Words that are mostly numbers/special chars
            elif len(re.findall(r'[^a-zA-Z\s]', word)) > len(word) * 0.7:
                gibberish_words += 1

        # If more than 30% gibberish words, consider it poor quality
        if words and (gibberish_words / len(words)) > 0.3:
            return True

        return False

    def select_best_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best OCR result based on confidence scoring.

        Args:
            results: List of OCR result dictionaries

        Returns:
            Best result dictionary
        """
        if not results:
            return {"text": "", "confidence": 0.0, "method": "none"}

        scores = self.score_ocr_results(results)

        # Find index of highest score
        best_index = scores.index(max(scores))

        best_result = results[best_index].copy()
        best_result["final_confidence"] = scores[best_index]

        return best_result

    def validate_drug_text(self, text: str) -> Dict[str, Any]:
        """
        Validate if extracted text contains valid drug information.

        Args:
            text: Text to validate

        Returns:
            Validation result with confidence and detected elements
        """
        validation = {
            "is_valid": False,
            "confidence": 0.0,
            "detected_elements": {
                "drug_name": False,
                "dosage": False,
                "ndc_code": False,
                "formulation": False
            },
            "issues": []
        }

        if not text:
            validation["issues"].append("No text extracted")
            return validation

        text_lower = text.lower()

        # Check for drug name
        drug_name_found = any(drug in text_lower for drug in self.drug_keywords)
        if drug_name_found:
            validation["detected_elements"]["drug_name"] = True

        # Check for dosage
        dosage_pattern = r'\b\d+\s*(mg|ml|mcg|units?|tablets?|capsules?)\b'
        if re.search(dosage_pattern, text, re.IGNORECASE):
            validation["detected_elements"]["dosage"] = True

        # Check for NDC code
        ndc_pattern = r'\b\d{4,5}-\d{3,4}-\d{1,2}\b|\b\d{10,11}\b'
        if re.search(ndc_pattern, text):
            validation["detected_elements"]["ndc_code"] = True

        # Check for formulation
        formulation_pattern = r'\b(tablet|capsule|pill|injection|syrup|cream|ointment)s?\b'
        if re.search(formulation_pattern, text, re.IGNORECASE):
            validation["detected_elements"]["formulation"] = True

        # Calculate overall confidence
        detected_count = sum(validation["detected_elements"].values())
        validation["confidence"] = detected_count / 4.0  # 4 possible elements

        # Determine if valid (at least drug name or dosage)
        validation["is_valid"] = (
            validation["detected_elements"]["drug_name"] or
            validation["detected_elements"]["dosage"]
        )

        if not validation["is_valid"]:
            validation["issues"].append("No drug name or dosage detected")

        return validation
