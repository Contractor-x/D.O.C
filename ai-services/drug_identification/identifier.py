"""
Drug Identifier Service
Identifies drugs from OCR text using multiple matching strategies.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher

from ..utils.api_client import APIClient
from .fuzzy_matcher import FuzzyMatcher
from .ndc_lookup import NDCLookup

logger = logging.getLogger(__name__)


class DrugIdentifier:
    """Service for identifying drugs from extracted text."""

    def __init__(self):
        self.api_client = APIClient()
        self.fuzzy_matcher = FuzzyMatcher()
        self.ndc_lookup = NDCLookup()

        # Common drug name mappings and corrections
        self.drug_corrections = {
            'hydrochlorothiazide': ['hydrochlorathiazide', 'hydrochlorthiazide'],
            'metformin': ['metformn', 'metformine'],
            'lisinopril': ['lisinpril', 'lisnopril'],
            'simvastatin': ['simvastin', 'simvastatina'],
            'omeprazole': ['omeprazol', 'omeprazle'],
            'amoxicillin': ['amoxicilin', 'amoxicllin'],
            'azithromycin': ['azithromicin', 'azithromyocin'],
        }

    async def identify_drug(self, ocr_text: str, ndc_code: Optional[str] = None) -> Dict:
        """
        Identify drug from OCR text and optional NDC code.

        Args:
            ocr_text: Text extracted from drug image
            ndc_code: Optional NDC code for verification

        Returns:
            Dict containing identification results
        """
        try:
            identification_results = {
                "identified": False,
                "drug_name": None,
                "confidence": 0.0,
                "ndc_match": False,
                "methods_used": [],
                "alternatives": [],
                "metadata": {}
            }

            # Method 1: NDC lookup if available
            if ndc_code:
                ndc_result = await self.ndc_lookup.lookup_by_ndc(ndc_code)
                if ndc_result["found"]:
                    identification_results.update({
                        "identified": True,
                        "drug_name": ndc_result["drug_name"],
                        "confidence": 0.95,
                        "ndc_match": True,
                        "methods_used": ["ndc_lookup"],
                        "metadata": ndc_result
                    })
                    return identification_results

            # Method 2: Direct text matching
            text_matches = self._identify_from_text(ocr_text)
            if text_matches:
                best_match = text_matches[0]  # Already sorted by confidence
                identification_results.update({
                    "identified": True,
                    "drug_name": best_match["drug_name"],
                    "confidence": best_match["confidence"],
                    "methods_used": ["text_matching"],
                    "alternatives": [m["drug_name"] for m in text_matches[1:]],
                    "metadata": {"matches": text_matches}
                })

            # Method 3: Fuzzy matching as fallback
            if not identification_results["identified"]:
                fuzzy_results = self.fuzzy_matcher.find_matches(ocr_text)
                if fuzzy_results:
                    best_fuzzy = fuzzy_results[0]
                    if best_fuzzy["similarity"] > 0.8:  # High confidence threshold
                        identification_results.update({
                            "identified": True,
                            "drug_name": best_fuzzy["drug_name"],
                            "confidence": best_fuzzy["similarity"] * 0.9,  # Slightly reduce confidence
                            "methods_used": ["fuzzy_matching"],
                            "alternatives": [m["drug_name"] for m in fuzzy_results[1:]],
                            "metadata": {"fuzzy_matches": fuzzy_results}
                        })

            # Method 4: API lookup for verification
            if identification_results["identified"]:
                api_verification = await self._verify_with_api(identification_results["drug_name"])
                if api_verification["verified"]:
                    identification_results["confidence"] = min(1.0, identification_results["confidence"] + 0.1)
                    identification_results["methods_used"].append("api_verification")
                    identification_results["metadata"]["api_data"] = api_verification

            return identification_results

        except Exception as e:
            logger.error(f"Drug identification failed: {e}")
            return {
                "identified": False,
                "drug_name": None,
                "confidence": 0.0,
                "error": str(e)
            }

    def _identify_from_text(self, text: str) -> List[Dict]:
        """
        Identify drugs using direct text pattern matching.

        Args:
            text: OCR extracted text

        Returns:
            List of potential drug matches with confidence scores
        """
        matches = []

        # Clean and normalize text
        clean_text = self._normalize_text(text)

        # Load drug database (in production, this would be from a real database)
        drug_database = self._load_drug_database()

        for drug_name, patterns in drug_database.items():
            confidence = 0.0

            # Check for exact matches
            for pattern in patterns:
                if re.search(pattern, clean_text, re.IGNORECASE):
                    confidence = 0.9  # High confidence for pattern match
                    break

            # Check for partial matches
            if confidence == 0.0:
                drug_words = drug_name.lower().split()
                text_words = clean_text.lower().split()

                matching_words = sum(1 for word in drug_words if word in text_words)
                if matching_words > 0:
                    confidence = min(0.8, matching_words / len(drug_words) * 0.7)

            if confidence > 0.3:  # Minimum threshold
                matches.append({
                    "drug_name": drug_name,
                    "confidence": confidence,
                    "match_type": "text_pattern" if confidence >= 0.8 else "partial_match"
                })

        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x["confidence"], reverse=True)

        return matches[:5]  # Return top 5 matches

    def _normalize_text(self, text: str) -> str:
        """Normalize OCR text for better matching."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Fix common OCR errors
        corrections = {
            'hydrochlorathiazide': 'hydrochlorothiazide',
            'hydrochlorthiazide': 'hydrochlorothiazide',
            'metformn': 'metformin',
            'metformine': 'metformin',
            'lisinpril': 'lisinopril',
            'lisnopril': 'lisinopril',
            'simvastin': 'simvastatin',
            'simvastatina': 'simvastatin',
            'omeprazol': 'omeprazole',
            'omeprazle': 'omeprazole',
            'amoxicilin': 'amoxicillin',
            'amoxicllin': 'amoxicillin',
            'azithromicin': 'azithromycin',
            'azithromyocin': 'azithromycin',
        }

        for incorrect, correct in corrections.items():
            text = re.sub(re.escape(incorrect), correct, text, flags=re.IGNORECASE)

        return text

    def _load_drug_database(self) -> Dict[str, List[str]]:
        """Load drug database with search patterns."""
        # In production, this would load from a database or API
        # For now, using a sample database
        return {
            "hydrochlorothiazide": [
                r'\bhydrochlorothiazide\b',
                r'\bhctz\b',
                r'\bhydrochlorothiazide\s+\d+\s*mg\b'
            ],
            "lisinopril": [
                r'\blisinopril\b',
                r'\bprinivil\b',
                r'\bzestril\b',
                r'\blisinopril\s+\d+\s*mg\b'
            ],
            "metformin": [
                r'\bmetformin\b',
                r'\bglucophage\b',
                r'\bmetformin\s+\d+\s*mg\b'
            ],
            "simvastatin": [
                r'\bsimvastatin\b',
                r'\bzocor\b',
                r'\bsimvastatin\s+\d+\s*mg\b'
            ],
            "omeprazole": [
                r'\bomeprazole\b',
                r'\bprilosec\b',
                r'\bomeprazole\s+\d+\s*mg\b'
            ],
            "amoxicillin": [
                r'\bamoxicillin\b',
                r'\btrimox\b',
                r'\bamoxil\b',
                r'\bamoxicillin\s+\d+\s*mg\b'
            ],
            "azithromycin": [
                r'\bazithromycin\b',
                r'\bzithromax\b',
                r'\bazithromycin\s+\d+\s*mg\b'
            ],
            "prednisone": [
                r'\bprednisone\b',
                r'\bdeltasone\b',
                r'\bprednisone\s+\d+\s*mg\b'
            ],
            "warfarin": [
                r'\bwarfarin\b',
                r'\bcoumadin\b',
                r'\bwarfarin\s+\d+\s*mg\b'
            ],
            "digoxin": [
                r'\bdigoxin\b',
                r'\blanoxin\b',
                r'\bdigoxin\s+\d+\s*mg\b'
            ]
        }

    async def _verify_with_api(self, drug_name: str) -> Dict:
        """
        Verify drug identification using external APIs.

        Args:
            drug_name: Drug name to verify

        Returns:
            Verification results
        """
        try:
            # This would integrate with OpenFDA or RxNorm APIs
            # For now, return mock verification
            return {
                "verified": True,
                "source": "openfda_api",
                "additional_info": {
                    "generic_name": drug_name,
                    "brand_names": [drug_name],  # Would be populated from API
                    "drug_class": "Unknown"  # Would be populated from API
                }
            }

        except Exception as e:
            logger.error(f"API verification failed: {e}")
            return {
                "verified": False,
                "error": str(e)
            }

    async def batch_identify(self, drug_texts: List[str]) -> List[Dict]:
        """
        Identify multiple drugs in batch.

        Args:
            drug_texts: List of OCR text strings

        Returns:
            List of identification results
        """
        tasks = [self.identify_drug(text) for text in drug_texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch identification failed for item {i}: {result}")
                processed_results.append({
                    "identified": False,
                    "drug_name": None,
                    "confidence": 0.0,
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results
