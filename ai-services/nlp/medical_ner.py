"""
Medical Named Entity Recognition using spaCy.
"""

import re
from typing import Dict, Any, List, Tuple
import spacy
from spacy.lang.en import English


class MedicalNER:
    """Extracts medical entities from text using spaCy and custom rules."""

    def __init__(self):
        """Initialize NER with spaCy model."""
        try:
            # Try to load medical model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic English model
            self.nlp = English()

        # Custom medical entity patterns
        self.drug_patterns = [
            r'\b(?:ibuprofen|acetaminophen|aspirin|amoxicillin|metformin|lisinopril|atorvastatin|levothyroxine|metoprolol|omeprazole|albuterol|prednisone|warfarin|clopidogrel|simvastatin|sertraline|escitalopram|citalopram|tramadol|hydrocodone|oxycodone|fentanyl|morphine|codeine|diazepam|lorazepam|alprazolam|zoloft|prozac|viagra|cialis|lipitor|plavix|singulair|advair|symbicort|lantus|humalog|novolog|januvia|onglyza|farxiga|invokana|jardiance)\b'
        ]

        self.dosage_patterns = [
            r'\b\d+(?:\.\d+)?\s*(?:mg|g|ml|l|mcg|units?|capsules?|tablets?|pills?)\b',
            r'\b\d+(?:\.\d+)?\s*(?:milligrams?|grams?|milliliters?|liters?|micrograms?)\b'
        ]

        self.frequency_patterns = [
            r'\b(?:once|twice|three times|four times)\s+(?:daily|a day|per day)\b',
            r'\b(?:every|q)\s*\d+\s*(?:hours?|hrs?)\b',
            r'\b(?:bid|tid|qid|prn|as needed)\b'
        ]

        self.condition_patterns = [
            r'\b(?:diabetes|hypertension|high blood pressure|depression|anxiety|asthma|copd|arthritis|rheumatoid arthritis|osteoarthritis|heart disease|coronary artery disease|stroke|cancer|breast cancer|lung cancer|prostate cancer|colorectal cancer|leukemia|lymphoma|multiple myeloma|melanoma|basal cell carcinoma|alzheimer|dementia|parkinson|epilepsy|seizures|migraine|headache|tension headache|cluster headache|fibromyalgia|chronic fatigue syndrome|ibs|irritable bowel syndrome|crohn|ulcerative colitis|gerd|acid reflux|peptic ulcer|hepatitis|cirrhosis|kidney disease|renal failure|uti|urinary tract infection|pneumonia|bronchitis|flu|influenza|cold|sinusitis|otitis media|pharyngitis|tonsillitis)\b'
        ]

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract medical entities from text.

        Args:
            text: Text to analyze

        Returns:
            Dict containing extracted entities
        """
        if not text:
            return {
                "text": text,
                "entities": [],
                "entity_counts": {},
                "confidence": 0.0
            }

        entities = []

        # Extract drugs
        drug_entities = self._extract_drugs(text)
        entities.extend(drug_entities)

        # Extract dosages
        dosage_entities = self._extract_dosages(text)
        entities.extend(dosage_entities)

        # Extract frequencies
        frequency_entities = self._extract_frequencies(text)
        entities.extend(frequency_entities)

        # Extract conditions
        condition_entities = self._extract_conditions(text)
        entities.extend(condition_entities)

        # Extract symptoms using spaCy
        symptom_entities = self._extract_symptoms_spacy(text)
        entities.extend(symptom_entities)

        # Count entities by type
        entity_counts = {}
        for entity in entities:
            entity_type = entity.get('type', 'unknown')
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        return {
            "text": text,
            "entities": entities,
            "entity_counts": entity_counts,
            "total_entities": len(entities),
            "confidence": self._calculate_confidence(entities)
        }

    def _extract_drugs(self, text: str) -> List[Dict[str, Any]]:
        """Extract drug names from text."""
        entities = []
        text_lower = text.lower()

        for pattern in self.drug_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                drug_name = match.group()
                # Find original case in text
                original_match = re.search(re.escape(drug_name), text, re.IGNORECASE)
                if original_match:
                    drug_name = original_match.group()

                entities.append({
                    "text": drug_name,
                    "type": "drug",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.95
                })

        return entities

    def _extract_dosages(self, text: str) -> List[Dict[str, Any]]:
        """Extract dosage information from text."""
        entities = []

        for pattern in self.dosage_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dosage = match.group()
                entities.append({
                    "text": dosage,
                    "type": "dosage",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.90
                })

        return entities

    def _extract_frequencies(self, text: str) -> List[Dict[str, Any]]:
        """Extract medication frequency information."""
        entities = []

        for pattern in self.frequency_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                frequency = match.group()
                entities.append({
                    "text": frequency,
                    "type": "frequency",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.85
                })

        return entities

    def _extract_conditions(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical conditions from text."""
        entities = []
        text_lower = text.lower()

        for pattern in self.condition_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                condition = match.group()
                # Find original case
                original_match = re.search(re.escape(condition), text, re.IGNORECASE)
                if original_match:
                    condition = original_match.group()

                entities.append({
                    "text": condition,
                    "type": "condition",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.88
                })

        return entities

    def _extract_symptoms_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract symptoms using spaCy NER."""
        entities = []

        try:
            doc = self.nlp(text)

            # Common symptom-related POS patterns
            symptom_patterns = [
                "pain", "ache", "hurt", "discomfort", "soreness",
                "nausea", "dizziness", "headache", "fever", "cough",
                "fatigue", "weakness", "swelling", "rash", "itching"
            ]

            for token in doc:
                if token.text.lower() in symptom_patterns:
                    entities.append({
                        "text": token.text,
                        "type": "symptom",
                        "start": token.idx,
                        "end": token.idx + len(token.text),
                        "confidence": 0.75
                    })

        except Exception:
            # If spaCy fails, return empty list
            pass

        return entities

    def _calculate_confidence(self, entities: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for entity extraction."""
        if not entities:
            return 0.0

        total_confidence = sum(entity.get('confidence', 0.0) for entity in entities)
        return total_confidence / len(entities)

    def extract_prescription_info(self, prescription_text: str) -> Dict[str, Any]:
        """
        Extract structured prescription information.

        Args:
            prescription_text: Prescription text

        Returns:
            Dict with structured prescription data
        """
        entities = self.extract_entities(prescription_text)

        # Structure prescription data
        prescription = {
            "drugs": [e for e in entities["entities"] if e["type"] == "drug"],
            "dosages": [e for e in entities["entities"] if e["type"] == "dosage"],
            "frequencies": [e for e in entities["entities"] if e["type"] == "frequency"],
            "conditions": [e for e in entities["entities"] if e["type"] == "condition"],
            "raw_text": prescription_text,
            "confidence": entities["confidence"]
        }

        return prescription
