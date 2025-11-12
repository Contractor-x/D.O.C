"""
Range Validator Service
Validates if prescribed dosages are within acceptable ranges.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class RangeValidator:
    """Service for validating dosage ranges and safety limits."""

    def __init__(self):
        # Safety limits for common drugs (max daily doses)
        self.safety_limits = {
            "acetaminophen": {
                "adult": 4000,  # mg/day
                "geriatric": 3000,
                "pediatric_mg_kg": 75
            },
            "ibuprofen": {
                "adult": 1200,
                "geriatric": 800,
                "pediatric_mg_kg": 40
            },
            "aspirin": {
                "adult": 4000,
                "geriatric": 2000,
                "pediatric_mg_kg": 100
            },
            "naproxen": {
                "adult": 1000,
                "geriatric": 750
            },
            "warfarin": {
                "adult": 10,  # mg/day
                "geriatric": 7.5
            },
            "digoxin": {
                "adult": 0.25,  # mg/day
                "geriatric": 0.125
            }
        }

        # Therapeutic ranges for drugs with narrow therapeutic index
        self.therapeutic_ranges = {
            "warfarin": {
                "target_inr": {"min": 2.0, "max": 3.0},
                "typical_dose_mg": {"min": 1, "max": 10}
            },
            "digoxin": {
                "serum_level_ng_ml": {"min": 0.8, "max": 2.0},
                "typical_dose_mg": {"min": 0.125, "max": 0.25}
            },
            "lithium": {
                "serum_level_meq_l": {"min": 0.6, "max": 1.2},
                "typical_dose_mg": {"min": 300, "max": 1200}
            },
            "theophylline": {
                "serum_level_mcg_ml": {"min": 8, "max": 15},
                "typical_dose_mg": {"min": 200, "max": 800}
            }
        }

    def validate_dosage_range(self, drug_name: str, prescribed_dose: Union[int, float],
                             patient_age: Union[int, float],
                             patient_weight_kg: Optional[float] = None,
                             frequency: Optional[str] = None) -> Dict:
        """
        Validate if a prescribed dosage is within safe and therapeutic ranges.

        Args:
            drug_name: Name of the drug
            prescribed_dose: Prescribed dose amount
            patient_age: Patient age in years
            patient_weight_kg: Patient weight in kg (optional)
            frequency: Dosing frequency (optional)

        Returns:
            Validation results
        """
        try:
            drug_lower = drug_name.lower()
            age_category = self._get_age_category(patient_age)

            validation = {
                "drug_name": drug_name,
                "prescribed_dose": prescribed_dose,
                "patient_age": patient_age,
                "age_category": age_category,
                "within_range": True,
                "warnings": [],
                "recommendations": [],
                "safety_status": "safe"
            }

            # Check safety limits
            safety_check = self._check_safety_limits(
                drug_lower, prescribed_dose, age_category, patient_weight_kg, frequency
            )
            if safety_check:
                validation["warnings"].extend(safety_check.get("warnings", []))
                if not safety_check.get("safe", True):
                    validation["within_range"] = False
                    validation["safety_status"] = "unsafe"

            # Check therapeutic ranges for narrow TI drugs
            therapeutic_check = self._check_therapeutic_range(drug_lower, prescribed_dose)
            if therapeutic_check:
                validation["warnings"].extend(therapeutic_check.get("warnings", []))
                validation["recommendations"].extend(therapeutic_check.get("recommendations", []))

            # Age-specific validations
            age_validation = self._validate_age_specific(drug_lower, prescribed_dose, patient_age)
            if age_validation:
                validation["warnings"].extend(age_validation.get("warnings", []))
                validation["recommendations"].extend(age_validation.get("recommendations", []))

            # Overall safety status
            if validation["warnings"]:
                if any("exceeds" in w.lower() or "above" in w.lower() for w in validation["warnings"]):
                    validation["safety_status"] = "unsafe"
                elif len(validation["warnings"]) > 2:
                    validation["safety_status"] = "caution"

            return validation

        except Exception as e:
            logger.error(f"Dosage range validation failed for {drug_name}: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e),
                "within_range": False,
                "safety_status": "unknown"
            }

    def _get_age_category(self, age: Union[int, float]) -> str:
        """Determine age category."""
        if age < 18:
            return "pediatric"
        elif age >= 65:
            return "geriatric"
        else:
            return "adult"

    def _check_safety_limits(self, drug_name: str, dose: Union[int, float],
                           age_category: str, weight_kg: Optional[float],
                           frequency: Optional[str]) -> Optional[Dict]:
        """Check against safety limits."""
        if drug_name not in self.safety_limits:
            return None

        limits = self.safety_limits[drug_name]
        warnings = []

        # Calculate daily dose if frequency provided
        daily_dose = self._calculate_daily_dose(dose, frequency)

        # Check limits based on age category
        if age_category == "pediatric" and f"{age_category}_mg_kg" in limits and weight_kg:
            max_per_kg = limits[f"{age_category}_mg_kg"]
            max_daily = weight_kg * max_per_kg
            if daily_dose > max_daily:
                warnings.append(f"Exceeds pediatric safety limit ({max_daily:.1f} mg/day)")

        elif age_category in limits:
            max_limit = limits[age_category]
            if daily_dose > max_limit:
                warnings.append(f"Exceeds {age_category} safety limit ({max_limit} mg/day)")

        return {
            "safe": len(warnings) == 0,
            "warnings": warnings
        }

    def _calculate_daily_dose(self, dose: Union[int, float], frequency: Optional[str]) -> float:
        """Calculate total daily dose based on frequency."""
        if not frequency:
            return dose  # Assume single daily dose

        freq_lower = frequency.lower()

        # Parse frequency patterns
        if "twice" in freq_lower or "bid" in freq_lower or "q12h" in freq_lower:
            return dose * 2
        elif "three" in freq_lower or "tid" in freq_lower or "q8h" in freq_lower:
            return dose * 3
        elif "four" in freq_lower or "qid" in freq_lower or "q6h" in freq_lower:
            return dose * 4
        elif "q4h" in freq_lower:
            return dose * 6
        elif "q3h" in freq_lower:
            return dose * 8
        elif "daily" in freq_lower or "once" in freq_lower:
            return dose
        else:
            return dose  # Default to as prescribed

    def _check_therapeutic_range(self, drug_name: str, dose: Union[int, float]) -> Optional[Dict]:
        """Check if dose is within therapeutic range for narrow TI drugs."""
        if drug_name not in self.therapeutic_ranges:
            return None

        drug_range = self.therapeutic_ranges[drug_name]
        warnings = []
        recommendations = []

        if "typical_dose_mg" in drug_range:
            dose_range = drug_range["typical_dose_mg"]
            if dose < dose_range["min"]:
                warnings.append(f"Dose below typical therapeutic range ({dose_range['min']}-{dose_range['max']} mg)")
                recommendations.append("Consider increasing dose with monitoring")
            elif dose > dose_range["max"]:
                warnings.append(f"Dose above typical therapeutic range ({dose_range['min']}-{dose_range['max']} mg)")
                recommendations.append("Monitor for toxicity signs")

        return {
            "warnings": warnings,
            "recommendations": recommendations
        }

    def _validate_age_specific(self, drug_name: str, dose: Union[int, float],
                             age: Union[int, float]) -> Optional[Dict]:
        """Perform age-specific validations."""
        warnings = []
        recommendations = []

        # Pediatric-specific checks
        if age < 18:
            if drug_name == "aspirin" and age < 18:
                warnings.append("Aspirin use in children under 18 associated with Reye's syndrome")
                recommendations.append("Avoid aspirin unless specifically indicated")

            elif drug_name == "tetracycline" and age < 8:
                warnings.append("Tetracycline can cause permanent tooth discoloration in children under 8")
                recommendations.append("Consider alternative antibiotics")

        # Geriatric-specific checks
        elif age >= 65:
            if drug_name in ["digoxin", "warfarin", "lithium"]:
                recommendations.append("Close monitoring required for narrow therapeutic index drug")

            if dose > 1000 and drug_name in ["acetaminophen", "ibuprofen"]:
                warnings.append("Higher doses in elderly increase risk of adverse effects")
                recommendations.append("Consider lower dose or alternative analgesics")

        return {
            "warnings": warnings,
            "recommendations": recommendations
        }

    def get_dosage_alerts(self, drug_name: str, dose: Union[int, float],
                         age: Union[int, float], conditions: Optional[List[str]] = None) -> List[Dict]:
        """
        Get dosage-related alerts and warnings.

        Args:
            drug_name: Name of the drug
            dose: Prescribed dose
            age: Patient age
            conditions: Patient conditions

        Returns:
            List of alert dictionaries
        """
        alerts = []
        drug_lower = drug_name.lower()
        conditions_lower = [c.lower() for c in conditions or []]

        # High-risk combinations
        if drug_lower == "warfarin" and any(c in ["aspirin", "nsaid"] for c in conditions_lower):
            alerts.append({
                "level": "critical",
                "message": "Warfarin + NSAID/aspirin increases bleeding risk significantly",
                "action": "Monitor INR closely, consider dose adjustment"
            })

        if drug_lower == "ace_inhibitor" and "hyperkalemia" in conditions_lower:
            alerts.append({
                "level": "high",
                "message": "ACE inhibitor may worsen hyperkalemia",
                "action": "Monitor potassium levels"
            })

        # Age-specific alerts
        if age >= 65 and dose > 2000 and drug_lower == "acetaminophen":
            alerts.append({
                "level": "moderate",
                "message": "High acetaminophen dose in elderly increases hepatotoxicity risk",
                "action": "Consider dose reduction or alternative"
            })

        return alerts

    def calculate_dose_adjustment(self, drug_name: str, current_dose: Union[int, float],
                                target_range: Dict, patient_factors: Dict) -> Dict:
        """
        Calculate dose adjustment needed to reach target range.

        Args:
            drug_name: Name of the drug
            current_dose: Current prescribed dose
            target_range: Target therapeutic range
            patient_factors: Patient-specific factors

        Returns:
            Dose adjustment recommendation
        """
        try:
            adjustment = {
                "drug_name": drug_name,
                "current_dose": current_dose,
                "target_range": target_range,
                "recommended_dose": None,
                "adjustment_factor": 1.0,
                "reasoning": []
            }

            # Age-based adjustments
            age = patient_factors.get("age", 50)
            if age >= 75:
                adjustment["adjustment_factor"] *= 0.75
                adjustment["reasoning"].append("Age ≥75 years: 25% reduction")

            # Renal function adjustments
            creatinine_clearance = patient_factors.get("creatinine_clearance")
            if creatinine_clearance:
                if creatinine_clearance < 30:
                    adjustment["adjustment_factor"] *= 0.5
                    adjustment["reasoning"].append("Severe renal impairment: 50% reduction")
                elif creatinine_clearance < 50:
                    adjustment["adjustment_factor"] *= 0.75
                    adjustment["reasoning"].append("Moderate renal impairment: 25% reduction")

            # Calculate recommended dose
            recommended = current_dose * adjustment["adjustment_factor"]
            adjustment["recommended_dose"] = round(recommended, 2)

            # Validate against target range
            if target_range:
                min_target = target_range.get("min")
                max_target = target_range.get("max")

                if min_target and recommended < min_target:
                    adjustment["recommended_dose"] = min_target
                    adjustment["reasoning"].append(f"Adjusted to minimum therapeutic dose ({min_target})")

                elif max_target and recommended > max_target:
                    adjustment["recommended_dose"] = max_target
                    adjustment["reasoning"].append(f"Capped at maximum therapeutic dose ({max_target})")

            return adjustment

        except Exception as e:
            logger.error(f"Dose adjustment calculation failed for {drug_name}: {e}")
            return {
                "error": str(e),
                "drug_name": drug_name,
                "current_dose": current_dose
            }
