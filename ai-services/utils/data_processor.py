
"""
Data processing utilities for medical data.
"""

import json
import csv
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from pathlib import Path


class DataProcessor:
    """Utilities for processing medical data."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text data.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove special characters but keep medical abbreviations
        text = text.replace('\n', ' ').replace('\t', ' ')

        return text.strip()

    @staticmethod
    def normalize_drug_name(drug_name: str) -> str:
        """
        Normalize drug names for consistent matching.

        Args:
            drug_name: Drug name to normalize

        Returns:
            Normalized drug name
        """
        if not drug_name:
            return ""

        # Convert to lowercase
        normalized = drug_name.lower().strip()

        # Remove common suffixes/prefixes that don't affect identification
        suffixes_to_remove = [' hcl', ' hydrochloride', ' sulfate', ' acetate', ' sodium', ' potassium']
        for suffix in suffixes_to_remove:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()

        return normalized

    @staticmethod
    def parse_dosage_string(dosage_str: str) -> Dict[str, Any]:
        """
        Parse dosage string into structured format.

        Args:
            dosage_str: Dosage string (e.g., "10 mg twice daily")

        Returns:
            Parsed dosage information
        """
        import re

        result = {
            "original": dosage_str,
            "amount": None,
            "unit": None,
            "frequency": None,
            "route": None
        }

        if not dosage_str:
            return result

        # Extract amount and unit
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|g|ml|l|mcg|units?|capsules?|tablets?|pills?)', dosage_str, re.IGNORECASE)
        if amount_match:
            result["amount"] = float(amount_match.group(1))
            result["unit"] = amount_match.group(2).lower()

        # Extract frequency
        freq_patterns = [
            (r'\b(?:once|single)\s+(?:a|per)\s+day\b', 'once daily'),
            (r'\b(?:twice|two times?)\s+(?:a|per)\s+day\b', 'twice daily'),
            (r'\b(?:three times?)\s+(?:a|per)\s+day\b', 'three times daily'),
            (r'\b(?:four times?)\s+(?:a|per)\s+day\b', 'four times daily'),
            (r'\b(?:every|q)\s*(\d+)\s*(?:hours?|hrs?)\b', 'every X hours'),
            (r'\bbid\b', 'twice daily'),
            (r'\btid\b', 'three times daily'),
            (r'\bqid\b', 'four times daily'),
            (r'\bprn\b', 'as needed'),
            (r'\bas needed\b', 'as needed')
        ]

        for pattern, freq in freq_patterns:
            if re.search(pattern, dosage_str, re.IGNORECASE):
                result["frequency"] = freq
                break

        # Extract route
        route_patterns = [
            r'\b(?:oral|by mouth|po)\b',
            r'\b(?:intravenous|iv|injection)\b',
            r'\b(?:subcutaneous|sq|subcut)\b',
            r'\b(?:intramuscular|im)\b',
            r'\b(?:topical|cream|ointment)\b',
            r'\b(?:inhaled|inhalation|nebulizer)\b'
        ]

        for pattern in route_patterns:
            match = re.search(pattern, dosage_str, re.IGNORECASE)
            if match:
                result["route"] = match.group().lower()
                break

        return result

    @staticmethod
    def validate_age_appropriateness(drug_name: str, age: int, conditions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate if a drug is age-appropriate.

        Args:
            drug_name: Name of the drug
            age: Patient age in years
            conditions: List of patient conditions

        Returns:
            Validation result
        """
        # This is a simplified version - in practice, this would use comprehensive drug databases
        result = {
            "drug": drug_name,
            "age": age,
            "is_appropriate": True,
            "warnings": [],
            "contraindications": []
        }

        # Age-based restrictions (simplified examples)
        age_restrictions = {
            "aspirin": {"min_age": 18, "warning": "Not recommended for children under 18 due to Reye's syndrome risk"},
            "tetracycline": {"min_age": 8, "warning": "Can cause permanent tooth discoloration in children"},
            "statins": {"min_age": 40, "warning": "Generally not recommended for children"},
            "benadryl": {"max_age": 65, "warning": "May cause excessive drowsiness in elderly"}
        }

        drug_lower = drug_name.lower()

        for drug_key, restriction in age_restrictions.items():
            if drug_key in drug_lower:
                if "min_age" in restriction and age < restriction["min_age"]:
                    result["is_appropriate"] = False
                    result["warnings"].append(restriction["warning"])
                elif "max_age" in restriction and age > restriction["max_age"]:
                    result["warnings"].append(restriction["warning"])

        return result

    @staticmethod
    def calculate_drug_interactions(drug_list: List[str]) -> List[Dict[str, Any]]:
        """
        Calculate potential drug interactions.

        Args:
            drug_list: List of drug names

        Returns:
            List of potential interactions
        """
        interactions = []

        # Simplified interaction checking - in practice, use comprehensive databases
        known_interactions = [
            {
                "drugs": ["warfarin", "aspirin"],
                "severity": "major",
                "description": "Increased risk of bleeding"
            },
            {
                "drugs": ["lisinopril", "potassium supplements"],
                "severity": "moderate",
                "description": "May increase potassium levels"
            },
            {
                "drugs": ["metformin", "furosemide"],
                "severity": "minor",
                "description": "May affect blood sugar control"
            }
        ]

        drug_set = set(d.lower() for d in drug_list)

        for interaction in known_interactions:
            interaction_drugs = set(d.lower() for d in interaction["drugs"])
            if len(interaction_drugs.intersection(drug_set)) >= 2:
                interactions.append({
                    "drugs_involved": list(interaction_drugs.intersection(drug_set)),
                    "severity": interaction["severity"],
                    "description": interaction["description"]
                })

        return interactions

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: Optional[List[str]] = None):
        """
        Export data to CSV file.

        Args:
            data: List of dictionaries to export
            filename: Output filename
            fieldnames: Column names (auto-detected if None)
        """
        if not data:
            return

        if not fieldnames:
            fieldnames = list(data[0].keys())

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def load_from_csv(filename: str) -> List[Dict[str, Any]]:
        """
        Load data from CSV file.

        Args:
            filename: Input filename

        Returns:
            List of dictionaries
        """
        data = []
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data

    @staticmethod
    def merge_drug_data(*data_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge drug data from multiple sources.

        Args:
            data_sources: Multiple lists of drug data

        Returns:
            Merged drug data
        """
        merged_data = {}
        all_keys = set()

        for source in data_sources:
            for item in source:
                drug_name = item.get('drug_name', item.get('name', ''))
                if drug_name:
                    normalized_name = DataProcessor.normalize_drug_name(drug_name)
                    if normalized_name not in merged_data:
                        merged_data[normalized_name] = {}

                    # Merge all fields
                    for key, value in item.items():
                        if key not in merged_data[normalized_name] or value:
                            merged_data[normalized_name][key] = value

                    all_keys.update(item.keys())

        # Convert back to list format
        result = []
        for drug_name, data in merged_data.items():
            data['drug_name'] = drug_name
            result.append(data)

        return result
