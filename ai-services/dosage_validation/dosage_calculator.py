"""
Dosage Calculator Service
Calculates appropriate drug dosages based on patient parameters.
"""

import logging
from typing import Dict, List, Optional, Union
import math

logger = logging.getLogger(__name__)


class DosageCalculator:
    """Service for calculating drug dosages based on patient parameters."""

    def __init__(self):
        # Standard dosage guidelines (mg/kg for weight-based, fixed for others)
        self.dosage_guidelines = {
            # Analgesics
            "acetaminophen": {
                "pediatric": {"dose_mg_kg": 10, "max_mg_kg_day": 75, "frequency": "q4-6h"},
                "adult": {"dose_mg": 500, "max_mg_day": 3000, "frequency": "q4-6h"},
                "geriatric": {"dose_mg": 325, "max_mg_day": 2000, "frequency": "q6h"}
            },
            "ibuprofen": {
                "pediatric": {"dose_mg_kg": 5, "max_mg_kg_day": 40, "frequency": "q6-8h"},
                "adult": {"dose_mg": 400, "max_mg_day": 1200, "frequency": "q6-8h"},
                "geriatric": {"dose_mg": 200, "max_mg_day": 800, "frequency": "q8h"}
            },

            # Antibiotics
            "amoxicillin": {
                "pediatric": {"dose_mg_kg": 25, "max_mg_kg_day": 100, "frequency": "q8h"},
                "adult": {"dose_mg": 500, "max_mg_day": 2000, "frequency": "q8h"},
                "geriatric": {"dose_mg": 500, "max_mg_day": 1500, "frequency": "q8h"}
            },
            "azithromycin": {
                "pediatric": {"dose_mg_kg": 10, "max_mg_kg_day": 10, "frequency": "daily"},
                "adult": {"dose_mg": 500, "max_mg_day": 500, "frequency": "daily"},
                "geriatric": {"dose_mg": 250, "max_mg_day": 250, "frequency": "daily"}
            },

            # Cardiovascular
            "lisinopril": {
                "adult": {"dose_mg": 10, "max_mg_day": 40, "frequency": "daily"},
                "geriatric": {"dose_mg": 5, "max_mg_day": 20, "frequency": "daily"}
            },
            "metoprolol": {
                "adult": {"dose_mg": 25, "max_mg_day": 200, "frequency": "daily"},
                "geriatric": {"dose_mg": 12.5, "max_mg_day": 100, "frequency": "daily"}
            },

            # Respiratory
            "albuterol": {
                "pediatric": {"dose_mg": 2.5, "max_mg_day": 10, "frequency": "q4-6h"},
                "adult": {"dose_mg": 2.5, "max_mg_day": 20, "frequency": "q4-6h"},
                "geriatric": {"dose_mg": 2.5, "max_mg_day": 15, "frequency": "q4-6h"}
            }
        }

    def calculate_dosage(self, drug_name: str, patient_age: Union[int, float],
                        patient_weight_kg: Optional[float] = None,
                        indication: Optional[str] = None,
                        renal_function: Optional[Dict] = None) -> Dict:
        """
        Calculate appropriate dosage for a drug based on patient parameters.

        Args:
            drug_name: Name of the drug
            patient_age: Patient age in years
            patient_weight_kg: Patient weight in kg (required for weight-based dosing)
            indication: Clinical indication (optional)
            renal_function: Renal function parameters (optional)

        Returns:
            Dosage calculation results
        """
        try:
            drug_lower = drug_name.lower()
            age_category = self._get_age_category(patient_age)

            if drug_lower not in self.dosage_guidelines:
                return {
                    "error": f"No dosage guidelines available for {drug_name}",
                    "drug_name": drug_name,
                    "patient_age": patient_age
                }

            guidelines = self.dosage_guidelines[drug_lower]
            age_guideline = guidelines.get(age_category, guidelines.get("adult", {}))

            if not age_guideline:
                return {
                    "error": f"No {age_category} dosage guidelines for {drug_name}",
                    "drug_name": drug_name,
                    "patient_age": patient_age
                }

            calculation = {
                "drug_name": drug_name,
                "patient_age": patient_age,
                "age_category": age_category,
                "guidelines": age_guideline,
                "calculated_dose": None,
                "max_daily_dose": None,
                "frequency": age_guideline.get("frequency", ""),
                "warnings": [],
                "adjustments": []
            }

            # Calculate dose
            if "dose_mg_kg" in age_guideline and patient_weight_kg:
                # Weight-based dosing
                dose_mg_kg = age_guideline["dose_mg_kg"]
                calculated_dose = patient_weight_kg * dose_mg_kg
                calculation["calculated_dose"] = round(calculated_dose, 1)
                calculation["dosing_method"] = "weight_based"
                calculation["weight_kg"] = patient_weight_kg

                # Calculate max daily dose
                if "max_mg_kg_day" in age_guideline:
                    max_daily = patient_weight_kg * age_guideline["max_mg_kg_day"]
                    calculation["max_daily_dose"] = round(max_daily, 1)

            elif "dose_mg" in age_guideline:
                # Fixed dosing
                calculation["calculated_dose"] = age_guideline["dose_mg"]
                calculation["dosing_method"] = "fixed"
                calculation["max_daily_dose"] = age_guideline.get("max_mg_day")

            # Apply renal adjustments if provided
            if renal_function:
                renal_adjustment = self._apply_renal_adjustment(
                    drug_name, calculation, renal_function
                )
                if renal_adjustment:
                    calculation["adjustments"].append(renal_adjustment)

            # Age-specific warnings
            age_warnings = self._get_age_warnings(drug_name, patient_age, calculation)
            calculation["warnings"].extend(age_warnings)

            return calculation

        except Exception as e:
            logger.error(f"Dosage calculation failed for {drug_name}: {e}")
            return {
                "error": str(e),
                "drug_name": drug_name,
                "patient_age": patient_age
            }

    def _get_age_category(self, age: Union[int, float]) -> str:
        """Determine age category for dosing."""
        if age < 18:
            return "pediatric"
        elif age >= 65:
            return "geriatric"
        else:
            return "adult"

    def _apply_renal_adjustment(self, drug_name: str, calculation: Dict,
                               renal_function: Dict) -> Optional[str]:
        """Apply renal dose adjustments."""
        creatinine_clearance = renal_function.get("creatinine_clearance")
        if not creatinine_clearance:
            return None

        drug_lower = drug_name.lower()

        # Drugs requiring renal adjustment
        renal_drugs = {
            "amoxicillin": {"threshold": 30, "adjustment": "Increase interval to q12h"},
            "azithromycin": {"threshold": 10, "adjustment": "Reduce dose by 50%"},
            "lisinopril": {"threshold": 30, "adjustment": "Reduce dose by 50%"},
            "metoprolol": {"threshold": 30, "adjustment": "Reduce dose by 50%"}
        }

        if drug_lower in renal_drugs:
            threshold = renal_drugs[drug_lower]["threshold"]
            if creatinine_clearance < threshold:
                adjustment = renal_drugs[drug_lower]["adjustment"]
                # Apply adjustment to calculated dose
                if calculation["dosing_method"] == "fixed" and calculation["calculated_dose"]:
                    if "50%" in adjustment:
                        calculation["calculated_dose"] = calculation["calculated_dose"] * 0.5
                return f"Renal adjustment: {adjustment} (CrCl {creatinine_clearance} mL/min)"

        return None

    def _get_age_warnings(self, drug_name: str, age: Union[int, float], calculation: Dict) -> List[str]:
        """Get age-specific warnings."""
        warnings = []
        drug_lower = drug_name.lower()

        # Pediatric warnings
        if age < 18:
            if drug_lower == "tetracycline" and age < 8:
                warnings.append("Tetracycline contraindicated in children under 8 years")
            elif drug_lower == "fluoroquinolones" and age < 18:
                warnings.append("Fluoroquinolones not recommended in children")

        # Geriatric warnings
        elif age >= 65:
            if drug_lower in ["amitriptyline", "diphenhydramine"]:
                warnings.append("Anticholinergic effects may cause confusion in elderly")
            elif calculation["dosing_method"] == "weight_based" and not calculation.get("weight_kg"):
                warnings.append("Weight-based dosing recommended for elderly patients")

        return warnings

    def validate_prescription_dosage(self, drug_name: str, prescribed_dose: str,
                                   patient_age: Union[int, float],
                                   patient_weight_kg: Optional[float] = None) -> Dict:
        """
        Validate if a prescribed dosage is appropriate.

        Args:
            drug_name: Name of the drug
            prescribed_dose: Prescribed dosage (e.g., "500mg", "10mg/kg")
            patient_age: Patient age
            patient_weight_kg: Patient weight (optional)

        Returns:
            Validation results
        """
        try:
            # Calculate recommended dosage
            recommended = self.calculate_dosage(drug_name, patient_age, patient_weight_kg)

            if "error" in recommended:
                return {
                    "valid": False,
                    "error": recommended["error"],
                    "prescribed_dose": prescribed_dose
                }

            # Parse prescribed dose
            parsed_dose = self._parse_dosage_string(prescribed_dose)
            if not parsed_dose:
                return {
                    "valid": False,
                    "error": "Could not parse prescribed dosage",
                    "prescribed_dose": prescribed_dose
                }

            validation = {
                "drug_name": drug_name,
                "prescribed_dose": prescribed_dose,
                "parsed_dose": parsed_dose,
                "recommended_dose": recommended.get("calculated_dose"),
                "max_daily_dose": recommended.get("max_daily_dose"),
                "valid": True,
                "warnings": [],
                "deviation": None
            }

            # Check if dose is within acceptable range
            if recommended.get("calculated_dose"):
                prescribed_value = parsed_dose.get("value", 0)
                recommended_value = recommended["calculated_dose"]

                # Calculate deviation percentage
                if recommended_value > 0:
                    deviation = ((prescribed_value - recommended_value) / recommended_value) * 100
                    validation["deviation"] = round(deviation, 1)

                    # Check for significant deviations
                    if abs(deviation) > 50:
                        validation["valid"] = False
                        validation["warnings"].append(f"Prescription deviates {abs(deviation)}% from recommended dose")
                    elif abs(deviation) > 20:
                        validation["warnings"].append(f"Prescription deviates {abs(deviation)}% from recommended dose")

            # Check maximum daily dose
            if recommended.get("max_daily_dose") and parsed_dose.get("value", 0) > recommended["max_daily_dose"]:
                validation["valid"] = False
                validation["warnings"].append("Prescribed dose exceeds maximum daily limit")

            return validation

        except Exception as e:
            logger.error(f"Dosage validation failed for {drug_name}: {e}")
            return {
                "valid": False,
                "error": str(e),
                "prescribed_dose": prescribed_dose
            }

    def _parse_dosage_string(self, dosage_str: str) -> Optional[Dict]:
        """Parse dosage string into value and unit."""
        import re

        # Match patterns like "500mg", "10mg/kg", "5ml", etc.
        pattern = r'(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|kg|iu|units?)(?:\s*/\s*(kg|day|dose))?'
        match = re.search(pattern, dosage_str.lower())

        if match:
            value = float(match.group(1))
            unit = match.group(2)
            denominator = match.group(3)

            return {
                "value": value,
                "unit": unit,
                "per_kg": denominator == "kg",
                "per_day": denominator == "day"
            }

        return None

    def get_dosage_range(self, drug_name: str, age: Union[int, float]) -> Dict:
        """
        Get acceptable dosage range for a drug and age.

        Args:
            drug_name: Name of the drug
            age: Patient age

        Returns:
            Dosage range information
        """
        calculation = self.calculate_dosage(drug_name, age)

        if "error" in calculation:
            return {"error": calculation["error"]}

        range_info = {
            "drug_name": drug_name,
            "age": age,
            "recommended_dose": calculation.get("calculated_dose"),
            "max_daily_dose": calculation.get("max_daily_dose"),
            "frequency": calculation.get("frequency"),
            "acceptable_range": None
        }

        # Calculate acceptable range (typically 80-120% of recommended)
        if calculation.get("calculated_dose"):
            recommended = calculation["calculated_dose"]
            min_acceptable = recommended * 0.8
            max_acceptable = recommended * 1.2

            range_info["acceptable_range"] = {
                "min": round(min_acceptable, 1),
                "max": round(max_acceptable, 1),
                "unit": "mg"  # Assuming mg, could be enhanced
            }

        return range_info
