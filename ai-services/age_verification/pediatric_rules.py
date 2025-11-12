"""
Pediatric Drug Safety Rules
Implements pediatric-specific drug safety guidelines.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class PediatricRules:
    """Service for pediatric drug safety verification."""

    def __init__(self):
        # Age groups in years
        self.age_groups = {
            "neonate": (0, 0.08),  # 0-1 month
            "infant": (0.08, 2),   # 1 month-2 years
            "toddler": (2, 6),     # 2-6 years
            "child": (6, 12),      # 6-12 years
            "adolescent": (12, 18) # 12-18 years
        }

        # Drugs contraindicated in pediatrics
        self.contraindicated_drugs = {
            "tetracycline": {
                "reason": "Discolors teeth and affects bone growth",
                "age_limit": 8  # Not for children under 8
            },
            "fluoroquinolones": {
                "reason": "Risk of cartilage damage",
                "age_limit": 18
            },
            "statins": {
                "reason": "Limited data in children, potential growth effects",
                "age_limit": 10
            }
        }

        # Weight-based dosing requirements
        self.weight_based_drugs = [
            "acetaminophen", "ibuprofen", "amoxicillin", "azithromycin",
            "prednisone", "albuterol", "insulin"
        ]

    def check_pediatric_safety(self, drug_name: str, dosage: str, age: Union[int, float],
                              conditions: Optional[List[str]] = None) -> Dict:
        """
        Check drug safety for pediatric patients.

        Args:
            drug_name: Name of the drug
            dosage: Drug dosage
            age: Patient age in years
            conditions: Patient conditions

        Returns:
            Safety assessment dictionary
        """
        assessment = {
            "safe": True,
            "risk_level": "low",
            "warnings": [],
            "recommendations": [],
            "age_group": self._get_age_group(age),
            "requires_weight_dosing": drug_name.lower() in self.weight_based_drugs
        }

        # Check age contraindications
        contraindication = self._check_contraindications(drug_name, age)
        if contraindication:
            assessment["safe"] = False
            assessment["risk_level"] = "high"
            assessment["warnings"].append(contraindication)

        # Check dosage appropriateness
        dosage_check = self._check_dosage_appropriateness(drug_name, dosage, age)
        if dosage_check:
            assessment["warnings"].extend(dosage_check.get("warnings", []))
            if not dosage_check.get("appropriate", True):
                assessment["safe"] = False
                assessment["risk_level"] = "moderate"

        # Check condition-specific warnings
        condition_warnings = self._check_condition_warnings(drug_name, conditions or [])
        if condition_warnings:
            assessment["warnings"].extend(condition_warnings)
            assessment["risk_level"] = "moderate"

        # Generate recommendations
        assessment["recommendations"] = self._generate_pediatric_recommendations(
            assessment, drug_name, age
        )

        return assessment

    def _get_age_group(self, age: Union[int, float]) -> str:
        """Determine pediatric age group."""
        for group, (min_age, max_age) in self.age_groups.items():
            if min_age <= age < max_age:
                return group
        return "adult"  # Over 18

    def _check_contraindications(self, drug_name: str, age: Union[int, float]) -> Optional[str]:
        """Check for drug contraindications in pediatrics."""
        drug_lower = drug_name.lower()

        for drug_pattern, info in self.contraindicated_drugs.items():
            if drug_pattern in drug_lower or drug_lower in drug_pattern:
                if age < info["age_limit"]:
                    return f"Contraindicated in children under {info['age_limit']} years: {info['reason']}"

        # Specific drug checks
        if drug_lower in ["aspirin", "salicylates"] and age < 18:
            return "Aspirin contraindicated in children under 18 due to Reye's syndrome risk"

        if "codeine" in drug_lower and age < 12:
            return "Codeine not recommended for children under 12 due to variable metabolism"

        return None

    def _check_dosage_appropriateness(self, drug_name: str, dosage: str, age: Union[int, float]) -> Optional[Dict]:
        """Check if dosage is appropriate for age."""
        if not dosage:
            return None

        drug_lower = drug_name.lower()
        warnings = []

        # Extract numeric dosage
        import re
        dosage_match = re.search(r'(\d+(?:\.\d+)?)', dosage)
        if not dosage_match:
            return None

        dose_value = float(dosage_match.group(1))

        # Age-specific dosage checks
        if drug_lower == "acetaminophen":
            if age < 2 and dose_value > 15:  # mg/kg
                warnings.append("Acetaminophen dose may be too high for infants")
            elif age >= 2 and dose_value > 10:  # mg/kg
                warnings.append("Acetaminophen dose may be too high for children")

        elif drug_lower == "ibuprofen":
            if age < 2:
                warnings.append("Ibuprofen not recommended for children under 2 years")
            elif dose_value > 10:  # mg/kg
                warnings.append("Ibuprofen dose may be too high")

        elif "amoxicillin" in drug_lower:
            if dose_value > 50:  # mg/kg
                warnings.append("Amoxicillin dose seems unusually high")

        return {
            "appropriate": len(warnings) == 0,
            "warnings": warnings
        }

    def _check_condition_warnings(self, drug_name: str, conditions: List[str]) -> List[str]:
        """Check for condition-specific warnings."""
        warnings = []
        drug_lower = drug_name.lower()
        conditions_lower = [c.lower() for c in conditions]

        # Asthma warnings
        if "asthma" in conditions_lower:
            if drug_lower in ["aspirin", "nsaids", "ibuprofen"]:
                warnings.append("NSAIDs may trigger asthma exacerbations")

        # Diabetes warnings
        if "diabetes" in conditions_lower:
            if "corticosteroid" in drug_lower or drug_lower == "prednisone":
                warnings.append("Corticosteroids may affect blood glucose control")

        # Seizure warnings
        if "seizures" in conditions_lower or "epilepsy" in conditions_lower:
            if drug_lower in ["bupropion", "tramadol"]:
                warnings.append("May lower seizure threshold")

        return warnings

    def _generate_pediatric_recommendations(self, assessment: Dict, drug_name: str, age: Union[int, float]) -> List[str]:
        """Generate pediatric-specific recommendations."""
        recommendations = []

        age_group = assessment.get("age_group", "child")

        # Weight-based dosing reminder
        if assessment.get("requires_weight_dosing", False):
            recommendations.append("Use weight-based dosing for accurate calculation")

        # Age-specific recommendations
        if age_group == "neonate":
            recommendations.append("Consult neonatologist for all medications")
            recommendations.append("Use oral syringes for accurate dosing")

        elif age_group == "infant":
            recommendations.append("Consult pediatrician for dosage verification")
            recommendations.append("Use appropriate formulation (liquid preferred)")

        elif age_group == "toddler":
            recommendations.append("Ensure medication is age-appropriate formulation")
            recommendations.append("Monitor for behavioral changes")

        elif age_group == "child":
            recommendations.append("Verify dosage based on current weight")
            recommendations.append("Consider taste and administration method")

        # General pediatric recommendations
        if age < 12:
            recommendations.append("Use liquid formulations when available")
            recommendations.append("Double-check dosage calculations")

        # Safety recommendations
        if not assessment.get("safe", True):
            recommendations.append("Consult pediatrician or pharmacist before administration")

        recommendations.append("Report any adverse reactions immediately")

        return recommendations

    def get_pediatric_dosage_guidelines(self, drug_name: str) -> Dict:
        """
        Get pediatric dosage guidelines for a drug.

        Args:
            drug_name: Name of the drug

        Returns:
            Dosage guidelines dictionary
        """
        drug_lower = drug_name.lower()

        guidelines = {
            "acetaminophen": {
                "neonate": "10-15 mg/kg every 6-8 hours",
                "infant": "10-15 mg/kg every 4-6 hours",
                "child": "10-15 mg/kg every 4-6 hours",
                "max_daily": "75 mg/kg/day"
            },
            "ibuprofen": {
                "infant": "5-10 mg/kg every 6-8 hours",
                "child": "5-10 mg/kg every 6-8 hours",
                "max_daily": "40 mg/kg/day"
            },
            "amoxicillin": {
                "neonate": "25-50 mg/kg/day divided every 12 hours",
                "infant": "20-40 mg/kg/day divided every 8 hours",
                "child": "25-50 mg/kg/day divided every 8 hours"
            }
        }

        return guidelines.get(drug_lower, {})

    def calculate_weight_based_dose(self, drug_name: str, weight_kg: float, age: Union[int, float]) -> Dict:
        """
        Calculate weight-based dosage for pediatric patients.

        Args:
            drug_name: Name of the drug
            weight_kg: Patient weight in kg
            age: Patient age in years

        Returns:
            Dosage calculation results
        """
        drug_lower = drug_name.lower()

        # Standard pediatric doses (mg/kg)
        standard_doses = {
            "acetaminophen": {
                "dose_mg_kg": 10,
                "frequency": "every 4-6 hours",
                "max_daily_mg_kg": 75
            },
            "ibuprofen": {
                "dose_mg_kg": 5,
                "frequency": "every 6-8 hours",
                "max_daily_mg_kg": 40
            },
            "amoxicillin": {
                "dose_mg_kg": 25,
                "frequency": "every 8 hours",
                "max_daily_mg_kg": 100
            },
            "azithromycin": {
                "dose_mg_kg": 10,
                "frequency": "once daily",
                "max_daily_mg_kg": 10
            }
        }

        if drug_lower not in standard_doses:
            return {
                "error": f"No weight-based dosing guidelines available for {drug_name}"
            }

        dose_info = standard_doses[drug_lower]
        calculated_dose = weight_kg * dose_info["dose_mg_kg"]
        max_daily = weight_kg * dose_info["max_daily_mg_kg"]

        return {
            "drug_name": drug_name,
            "weight_kg": weight_kg,
            "calculated_dose_mg": round(calculated_dose, 1),
            "max_daily_dose_mg": round(max_daily, 1),
            "frequency": dose_info["frequency"],
            "age_appropriate": self._is_age_appropriate_for_dose(drug_name, age)
        }

    def _is_age_appropriate_for_dose(self, drug_name: str, age: Union[int, float]) -> bool:
        """Check if age is appropriate for standard dosing."""
        drug_lower = drug_name.lower()

        # Age restrictions
        restrictions = {
            "ibuprofen": 2,  # Not for under 2 years
            "tetracycline": 8,  # Not for under 8 years
        }

        min_age = restrictions.get(drug_lower, 0)
        return age >= min_age
