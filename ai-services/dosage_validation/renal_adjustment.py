"""
Renal Adjustment Service
Calculates dosage adjustments for patients with renal impairment.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class RenalAdjustment:
    """Service for renal dose adjustments based on creatinine clearance."""

    def __init__(self):
        # Renal dosing adjustments based on creatinine clearance (CrCl)
        self.renal_adjustments = {
            "amoxicillin": {
                "normal": {"dose": "500mg q8h", "max": "2000mg/day"},
                "mild": {"dose": "500mg q8h", "max": "2000mg/day"},  # CrCl 50-80
                "moderate": {"dose": "500mg q12h", "max": "1000mg/day"},  # CrCl 30-50
                "severe": {"dose": "500mg q24h", "max": "500mg/day"}  # CrCl <30
            },
            "azithromycin": {
                "normal": {"dose": "500mg daily", "max": "500mg/day"},
                "mild": {"dose": "500mg daily", "max": "500mg/day"},
                "moderate": {"dose": "250mg daily", "max": "250mg/day"},
                "severe": {"dose": "250mg q48h", "max": "250mg q48h"}
            },
            "lisinopril": {
                "normal": {"dose": "10mg daily", "max": "40mg/day"},
                "mild": {"dose": "5mg daily", "max": "20mg/day"},
                "moderate": {"dose": "2.5mg daily", "max": "10mg/day"},
                "severe": {"dose": "2.5mg q48h", "max": "5mg q48h"}
            },
            "metoprolol": {
                "normal": {"dose": "25-100mg daily", "max": "200mg/day"},
                "mild": {"dose": "25-50mg daily", "max": "100mg/day"},
                "moderate": {"dose": "12.5-25mg daily", "max": "50mg/day"},
                "severe": {"dose": "12.5mg daily", "max": "25mg/day"}
            },
            "warfarin": {
                "normal": {"dose": "2.5-10mg daily", "monitoring": "INR q1-2 weeks"},
                "mild": {"dose": "2.5-7.5mg daily", "monitoring": "INR q1 week"},
                "moderate": {"dose": "1.25-5mg daily", "monitoring": "INR q3-5 days"},
                "severe": {"dose": "1.25-2.5mg daily", "monitoring": "INR daily initially"}
            },
            "digoxin": {
                "normal": {"dose": "0.125-0.25mg daily", "monitoring": "Serum level"},
                "mild": {"dose": "0.125mg daily", "monitoring": "Serum level"},
                "moderate": {"dose": "0.0625-0.125mg daily", "monitoring": "Serum level"},
                "severe": {"dose": "0.0625mg q48h", "monitoring": "Serum level"}
            },
            "lithium": {
                "normal": {"dose": "300-600mg bid", "monitoring": "Serum level"},
                "mild": {"dose": "150-300mg bid", "monitoring": "Serum level q1 week"},
                "moderate": {"dose": "150mg bid", "monitoring": "Serum level q3 days"},
                "severe": {"dose": "150mg daily", "monitoring": "Serum level daily"}
            }
        }

        # Drugs that are renally cleared and require adjustment
        self.renal_drugs = set(self.renal_adjustments.keys())

    def calculate_renal_adjustment(self, drug_name: str, creatinine_clearance: Union[int, float],
                                 current_dose: Optional[Union[int, float]] = None) -> Dict:
        """
        Calculate renal dose adjustment for a drug.

        Args:
            drug_name: Name of the drug
            creatinine_clearance: Creatinine clearance in mL/min
            current_dose: Current prescribed dose (optional)

        Returns:
            Renal adjustment recommendations
        """
        try:
            drug_lower = drug_name.lower()

            if drug_lower not in self.renal_adjustments:
                return {
                    "drug_name": drug_name,
                    "requires_adjustment": False,
                    "reason": "Drug does not require renal dose adjustment"
                }

            # Determine renal function category
            renal_category = self._classify_renal_function(creatinine_clearance)

            adjustment = self.renal_adjustments[drug_lower][renal_category]

            result = {
                "drug_name": drug_name,
                "creatinine_clearance": creatinine_clearance,
                "renal_category": renal_category,
                "requires_adjustment": renal_category != "normal",
                "recommended_dose": adjustment.get("dose"),
                "max_daily_dose": adjustment.get("max"),
                "monitoring": adjustment.get("monitoring"),
                "warnings": [],
                "recommendations": []
            }

            # Add warnings and recommendations
            if renal_category == "severe":
                result["warnings"].append("Severe renal impairment - close monitoring required")
                result["recommendations"].append("Consider alternative drug if possible")

            elif renal_category == "moderate":
                result["warnings"].append("Moderate renal impairment - dose reduction required")
                result["recommendations"].append("Monitor renal function regularly")

            # Check if current dose exceeds recommendations
            if current_dose and renal_category != "normal":
                max_dose = self._extract_numeric_dose(adjustment.get("max", ""))
                if max_dose and current_dose > max_dose:
                    result["warnings"].append(f"Current dose ({current_dose}mg) exceeds renal-adjusted maximum ({max_dose}mg)")

            return result

        except Exception as e:
            logger.error(f"Renal adjustment calculation failed for {drug_name}: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e),
                "requires_adjustment": False
            }

    def _classify_renal_function(self, crcl: Union[int, float]) -> str:
        """Classify renal function based on creatinine clearance."""
        if crcl >= 80:
            return "normal"
        elif crcl >= 50:
            return "mild"
        elif crcl >= 30:
            return "moderate"
        else:
            return "severe"

    def _extract_numeric_dose(self, dose_str: str) -> Optional[float]:
        """Extract numeric dose from dose string."""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', dose_str)
        return float(match.group(1)) if match else None

    def get_renal_dosing_guidelines(self, drug_name: str) -> Dict:
        """
        Get complete renal dosing guidelines for a drug.

        Args:
            drug_name: Name of the drug

        Returns:
            Renal dosing guidelines
        """
        drug_lower = drug_name.lower()

        if drug_lower not in self.renal_adjustments:
            return {
                "drug_name": drug_name,
                "requires_renal_adjustment": False
            }

        guidelines = self.renal_adjustments[drug_lower]

        return {
            "drug_name": drug_name,
            "requires_renal_adjustment": True,
            "normal_renal_function": guidelines["normal"],
            "mild_impairment": guidelines["mild"],  # CrCl 50-80 mL/min
            "moderate_impairment": guidelines["moderate"],  # CrCl 30-50 mL/min
            "severe_impairment": guidelines["severe"]  # CrCl <30 mL/min
        }

    def batch_renal_adjustments(self, prescriptions: List[Dict]) -> List[Dict]:
        """
        Calculate renal adjustments for multiple prescriptions.

        Args:
            prescriptions: List of prescription dicts with drug_name, dose, crcl

        Returns:
            List of renal adjustment results
        """
        results = []

        for prescription in prescriptions:
            drug_name = prescription.get("drug_name", "")
            crcl = prescription.get("creatinine_clearance", 80)
            current_dose = prescription.get("current_dose")

            adjustment = self.calculate_renal_adjustment(drug_name, crcl, current_dose)
            results.append(adjustment)

        return results

    def estimate_creatinine_clearance(self, age: Union[int, float], weight_kg: float,
                                    serum_creatinine: float, gender: str = "male") -> float:
        """
        Estimate creatinine clearance using Cockcroft-Gault equation.

        Args:
            age: Age in years
            weight_kg: Weight in kg
            serum_creatinine: Serum creatinine in mg/dL
            gender: "male" or "female"

        Returns:
            Estimated creatinine clearance in mL/min
        """
        try:
            # Cockcroft-Gault equation
            # CrCl = (140 - age) × weight × (0.85 if female) / (72 × serum_creatinine)

            gender_factor = 0.85 if gender.lower() == "female" else 1.0

            crcl = ((140 - age) * weight_kg * gender_factor) / (72 * serum_creatinine)

            return round(crcl, 1)

        except Exception as e:
            logger.error(f"Creatinine clearance estimation failed: {e}")
            return 80.0  # Default to normal

    def get_renal_monitoring_schedule(self, drug_name: str, renal_category: str) -> Dict:
        """
        Get monitoring schedule for renally adjusted drugs.

        Args:
            drug_name: Name of the drug
            renal_category: Renal function category

        Returns:
            Monitoring recommendations
        """
        drug_lower = drug_name.lower()

        if drug_lower not in self.renal_adjustments:
            return {"monitoring_required": False}

        base_monitoring = {
            "normal": {
                "frequency": "Routine monitoring",
                "parameters": ["Renal function annually"]
            },
            "mild": {
                "frequency": "Every 6-12 months",
                "parameters": ["Creatinine clearance", "Serum creatinine"]
            },
            "moderate": {
                "frequency": "Every 3-6 months",
                "parameters": ["Creatinine clearance", "Serum creatinine", "Electrolytes"]
            },
            "severe": {
                "frequency": "Monthly or more frequent",
                "parameters": ["Creatinine clearance", "Serum creatinine", "Electrolytes", "Drug levels if applicable"]
            }
        }

        monitoring = base_monitoring.get(renal_category, base_monitoring["normal"])

        # Drug-specific monitoring
        drug_specific = self.renal_adjustments[drug_lower][renal_category]
        if "monitoring" in drug_specific:
            monitoring["drug_specific"] = drug_specific["monitoring"]

        return monitoring

    def validate_renal_dose(self, drug_name: str, prescribed_dose: Union[int, float],
                          creatinine_clearance: Union[int, float]) -> Dict:
        """
        Validate if prescribed dose is appropriate for renal function.

        Args:
            drug_name: Name of the drug
            prescribed_dose: Prescribed dose
            creatinine_clearance: Creatinine clearance

        Returns:
            Validation results
        """
        try:
            adjustment = self.calculate_renal_adjustment(drug_name, creatinine_clearance, prescribed_dose)

            validation = {
                "drug_name": drug_name,
                "prescribed_dose": prescribed_dose,
                "creatinine_clearance": creatinine_clearance,
                "valid": True,
                "warnings": [],
                "recommendations": []
            }

            if adjustment.get("requires_adjustment"):
                max_dose = self._extract_numeric_dose(adjustment.get("max_daily_dose", ""))
                if max_dose and prescribed_dose > max_dose:
                    validation["valid"] = False
                    validation["warnings"].append(f"Dose exceeds renal-adjusted maximum ({max_dose}mg)")
                    validation["recommendations"].append(f"Reduce dose to ≤{max_dose}mg daily")

                validation["recommendations"].append(f"Recommended: {adjustment.get('recommended_dose', 'Consult pharmacist')}")

            return validation

        except Exception as e:
            logger.error(f"Renal dose validation failed for {drug_name}: {e}")
            return {
                "drug_name": drug_name,
                "valid": False,
                "error": str(e)
            }
