"""
Drug OCR Service
Handles optical character recognition for drug labels and packaging.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import io

import pytesseract
import cv2
import numpy as np
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account

from ..utils.api_client import APIClient
from .preprocessing import ImagePreprocessor
from .confidence_scorer import ConfidenceScorer

logger = logging.getLogger(__name__)


class DrugOCR:
    """OCR service for drug identification from images."""

    def __init__(self, google_vision_key: Optional[str] = None):
        self.preprocessor = ImagePreprocessor()
        self.confidence_scorer = ConfidenceScorer()
        self.api_client = APIClient()

        # Initialize Google Vision client if key provided
        self.vision_client = None
        if google_vision_key:
            try:
                credentials = service_account.Credentials.from_service_account_info(
                    {"private_key": google_vision_key, "client_email": "", "token_uri": ""}
                )
                self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
            except Exception as e:
                logger.warning(f"Failed to initialize Google Vision: {e}")

    async def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extract text from drug image using multiple OCR methods.

        Args:
            image_path: Path to the image file

        Returns:
            Dict containing extracted text and confidence scores
        """
        try:
            # Read and preprocess image
            image = Image.open(image_path)
            processed_image = self.preprocessor.preprocess_for_ocr(image)

            # Extract text using Tesseract
            tesseract_result = self._extract_with_tesseract(processed_image)

            # Extract text using Google Vision if available
            vision_result = None
            if self.vision_client:
                vision_result = await self._extract_with_google_vision(image_path)

            # Combine results
            combined_result = self._combine_ocr_results(tesseract_result, vision_result)

            return {
                "success": True,
                "text": combined_result["text"],
                "confidence": combined_result["confidence"],
                "method": combined_result["method"],
                "raw_results": {
                    "tesseract": tesseract_result,
                    "google_vision": vision_result
                }
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }

    def _extract_with_tesseract(self, image: Image.Image) -> Dict:
        """Extract text using Tesseract OCR."""
        try:
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

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
                "text": extracted_text,
                "confidence": avg_confidence / 100.0,  # Normalize to 0-1
                "method": "tesseract"
            }

        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return {"text": "", "confidence": 0.0, "method": "tesseract", "error": str(e)}

    async def _extract_with_google_vision(self, image_path: str) -> Optional[Dict]:
        """Extract text using Google Cloud Vision API."""
        if not self.vision_client:
            return None

        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.vision_client.text_detection(image=image)

            if response.error.message:
                logger.error(f"Google Vision error: {response.error.message}")
                return None

            texts = response.text_annotations
            if not texts:
                return {"text": "", "confidence": 0.0, "method": "google_vision"}

            # Get the full text and confidence
            full_text = texts[0].description
            confidence = texts[0].bounding_poly  # Vision API doesn't provide confidence for text

            return {
                "text": full_text,
                "confidence": 0.8,  # Google Vision typically has high accuracy
                "method": "google_vision"
            }

        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return {"text": "", "confidence": 0.0, "method": "google_vision", "error": str(e)}

    def _combine_ocr_results(self, tesseract: Dict, vision: Optional[Dict]) -> Dict:
        """Combine results from multiple OCR methods."""
        if not vision or vision.get("confidence", 0) < 0.5:
            return tesseract

        # Use confidence scorer to determine best result
        scores = self.confidence_scorer.score_ocr_results([tesseract, vision])

        if scores[0] >= scores[1]:
            return tesseract
        else:
            return vision

    async def extract_drug_info(self, image_path: str) -> Dict:
        """
        Extract drug information from image including name, dosage, NDC code.

        Args:
            image_path: Path to drug image

        Returns:
            Dict with extracted drug information
        """
        ocr_result = await self.extract_text_from_image(image_path)

        if not ocr_result["success"]:
            return ocr_result

        text = ocr_result["text"]

        # Extract drug name (typically the most prominent text)
        drug_name = self._extract_drug_name(text)

        # Extract dosage information
        dosage = self._extract_dosage(text)

        # Extract NDC code
        ndc_code = self._extract_ndc_code(text)

        return {
            "success": True,
            "drug_name": drug_name,
            "dosage": dosage,
            "ndc_code": ndc_code,
            "confidence": ocr_result["confidence"],
            "raw_text": text
        }

    def _extract_drug_name(self, text: str) -> Optional[str]:
        """Extract drug name from OCR text."""
        # Simple heuristic: look for capitalized words that might be drug names
        words = text.split()
        potential_names = []

        for word in words:
            if len(word) > 3 and word[0].isupper():
                potential_names.append(word)

        return ' '.join(potential_names[:3]) if potential_names else None

    def _extract_dosage(self, text: str) -> Optional[str]:
        """Extract dosage information from OCR text."""
        import re

        # Look for dosage patterns like "10mg", "5 ml", "100 units"
        dosage_patterns = [
            r'\d+\s*mg',
            r'\d+\s*ml',
            r'\d+\s*units?',
            r'\d+\s*mcg',
            r'\d+\.\d+\s*mg'
        ]

        for pattern in dosage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()

        return None

    def _extract_ndc_code(self, text: str) -> Optional[str]:
        """Extract NDC code from OCR text."""
        import re

        # NDC codes are typically 10-11 digits with dashes: XXX-XX-XXXX or XXXXXXXXXX
        ndc_patterns = [
            r'\d{4,5}-\d{3,4}-\d{1,2}',
            r'\d{10,11}'
        ]

        for pattern in ndc_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()

        return None
