"""
Geriatric Drug Safety Rules
Implements Beers Criteria and geriatric-specific drug safety guidelines.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class GeriatricRules:
    """Service for geriatric drug safety verification using Beers Criteria."""

    def __init__(self):
        # Beers Criteria drugs to avoid in elderly
        self.beers_criteria_drugs = {
            "amitriptyline": {
                "reason": "Strong anticholinergic effects, sedation",
                "alternative": "escitalopram, sertraline"
            },
            "diphenhydramine": {
                "reason": "Strong anticholinergic effects, confusion",
                "alternative": "loratadine, cetirizine"
            },
            "doxepin": {
                "reason": "Strong anticholinergic and sedative effects",
                "alternative": "eszopiclone, zolpidem"
            },
            "hydroxyzine": {
                "reason": "Strong anticholinergic effects",
                "alternative": "hydrocortisone cream"
            },
            "meperidine": {
                "reason": "Risk of delirium, better alternatives available",
                "alternative": "morphine, oxycodone"
            },
            "pentazocine": {
                "reason": "Risk of delirium, better alternatives available",
                "alternative": "morphine, oxycodone"
            },
            "trimethobenzamide": {
                "reason": "Strong anticholinergic effects",
                "alternative": "ondansetron, promethazine"
            }
        }

        # Drugs requiring dose adjustment in elderly
        self.dose_adjustment_drugs = {
            "warfarin": {
                "adjustment": "Reduce dose by 20-30%",
                "monitoring": "INR monitoring required"
            },
            "digoxin": {
                "adjustment": "Reduce dose by 50%",
                "monitoring": "Serum levels monitoring"
            },
            "lithium": {
                "adjustment": "Reduce dose by 50-75%",
                "monitoring": "Serum levels monitoring"
            },
            "theophylline": {
                "adjustment": "Reduce dose by 50%",
                "monitoring": "Serum levels monitoring"
            }
        }

        # High-risk drug combinations in elderly
        self.high_risk_combinations = [
            {
                "drugs": ["warfarin", "aspirin"],
                "risk": "Increased bleeding risk",
                "recommendation": "Avoid combination if possible"
            },
            {
                "drugs": ["ace_inhibitor", "potassium_supplement"],
                "risk": "Hyperkalemia",
                "recommendation": "Monitor potassium levels"
            },
            {
                "drugs": ["nsaid", "ace_inhibitor"],
                "risk": "Acute kidney injury",
                "recommendation": "Monitor renal function"
            }
        ]

    def check_geriatric_safety(self, drug_name: str, dosage: str, age: Union[int, float],
                               conditions: Optional[List[str]] = None) -> Dict:
        """
        Check drug safety for geriatric patients using Beers Criteria.

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
            "beers_criteria_violation": False,
            "requires_dose_adjustment": False
        }

        # Check Beers Criteria
        beers_check = self._check_beers_criteria(drug_name)
        if beers_check:
            assessment["safe"] = False
            assessment["risk_level"] = "high"
            assessment["warnings"].append(beers_check["warning"])
            assessment["recommendations"].append(beers_check["recommendation"])
            assessment["beers_criteria_violation"] = True

        # Check dose adjustment requirements
        dose_check = self._check_dose_adjustment(drug_name, age)
        if dose_check:
            assessment["requires_dose_adjustment"] = True
            assessment["warnings"].append(dose_check["warning"])
            assessment["recommendations"].append(dose_check["recommendation"])
            if assessment["risk_level"] == "low":
                assessment["risk_level"] = "moderate"

        # Check drug interactions
        interaction_check = self._check_drug_interactions(drug_name, conditions or [])
        if interaction_check:
            assessment["warnings"].extend(interaction_check["warnings"])
            assessment["recommendations"].extend(interaction_check["recommendations"])
            if assessment["risk_level"] == "low":
                assessment["risk_level"] = "moderate"

        # Age-specific considerations
        age_considerations = self._check_age_considerations(age)
        if age_considerations:
            assessment["warnings"].extend(age_considerations["warnings"])
            assessment["recommendations"].extend(age_considerations["recommendations"])

        return assessment

    def _check_beers_criteria(self, drug_name: str) -> Optional[Dict]:
        """Check if drug violates Beers Criteria."""
        drug_lower = drug_name.lower()

        for drug, info in self.beers_criteria_drugs.items():
            if drug in drug_lower:
                return {
                    "warning": f"Beers Criteria: Avoid in elderly - {info['reason']}",
                    "recommendation": f"Consider alternative: {info['alternative']}"
                }

        # Check for drug classes
        if any(term in drug_lower for term in ["anticholinergic", "antihistamine"]):
            return {
                "warning": "Beers Criteria: Avoid anticholinergics in elderly due to confusion risk",
                "recommendation": "Use non-anticholinergic alternatives when possible"
            }

        return None

    def _check_dose_adjustment(self, drug_name: str, age: Union[int, float]) -> Optional[Dict]:
        """Check if drug requires dose adjustment in elderly."""
        drug_lower = drug_name.lower()

        for drug, info in self.dose_adjustment_drugs.items():
            if drug in drug_lower:
                return {
                    "warning": f"Requires dose adjustment in elderly: {info['adjustment']}",
                    "recommendation": f"{info['monitoring']} required"
                }

        # General dose adjustment for age > 75
        if age > 75:
            return {
                "warning": "Consider dose reduction in patients over 75 years",
                "recommendation": "Start with lowest effective dose and titrate carefully"
            }

        return None

    def _check_drug_interactions(self, drug_name: str, conditions: List[str]) -> Optional[Dict]:
        """Check for high-risk drug combinations and conditions."""
        warnings = []
        recommendations = []

        drug_lower = drug_name.lower()
        conditions_lower = [c.lower() for c in conditions]

        # Check specific combinations
        for combo in self.high_risk_combinations:
            drug_match = any(drug in drug_lower for drug in combo["drugs"])
            if drug_match:
                warnings.append(f"High-risk combination: {combo['risk']}")
                recommendations.append(combo["recommendation"])

        # Condition-specific warnings
        if "heart_failure" in conditions_lower:
            if any(drug in drug_lower for drug in ["nsaid", "ibuprofen", "naproxen"]):
                warnings.append("NSAIDs may exacerbate heart failure")
                recommendations.append("Avoid NSAIDs or use with extreme caution")

        if "kidney_disease" in conditions_lower or "renal_impairment" in conditions_lower:
            if any(drug in drug_lower for drug in ["nsaid", "aminoglycoside", "ace_inhibitor"]):
                warnings.append("Drug may worsen renal function")
                recommendations.append("Monitor renal function closely")

        if "dementia" in conditions_lower or "cognitive_impairment" in conditions_lower:
            if any(drug in drug_lower for drug in ["anticholinergic", "benzodiazepine", "antipsychotic"]):
                warnings.append("May worsen cognitive impairment")
                recommendations.append("Use with caution, monitor cognition")

        return {
            "warnings": warnings,
            "recommendations": recommendations
        } if warnings else None

    def _check_age_considerations(self, age: Union[int, float]) -> Optional[Dict]:
        """Check age-specific considerations for elderly patients."""
        warnings = []
        recommendations = []

        if age > 85:
            warnings.append("Very elderly patient (>85 years) - increased sensitivity to medications")
            recommendations.append("Start with 50% of usual adult dose")
            recommendations.append("Monitor closely for adverse effects")

        elif age > 75:
            warnings.append("Elderly patient (>75 years) - consider dose reduction")
            recommendations.append("Reduce dose by 25-50% from adult dose")

        # General geriatric considerations
        recommendations.extend([
            "Monitor for orthostatic hypotension",
            "Assess fall risk before starting new medications",
            "Review all medications regularly for discontinuation opportunities"
        ])

        return {
            "warnings": warnings,
            "recommendations": recommendations
        } if warnings or recommendations else None

    def get_beers_criteria_alternatives(self, drug_name: str) -> List[Dict]:
        """
        Get alternative medications for Beers Criteria drugs.

        Args:
            drug_name: Name of the drug to find alternatives for

        Returns:
            List of alternative medications
        """
        drug_lower = drug_name.lower()
        alternatives = []

        for drug, info in self.beers_criteria_drugs.items():
            if drug in drug_lower:
                alternatives.append({
                    "original_drug": drug_name,
                    "alternative": info["alternative"],
                    "reason": info["reason"],
                    "category": "beers_criteria"
                })

        return alternatives

    def calculate_geriatric_dose(self, drug_name: str, standard_dose: str, age: Union[int, float],
                                weight_kg: Optional[float] = None, creatinine_clearance: Optional[float] = None) -> Dict:
        """
        Calculate appropriate dose for geriatric patients.

        Args:
            drug_name: Name of the drug
            standard_dose: Standard adult dose
            age: Patient age
            weight_kg: Patient weight (optional)
            creatinine_clearance: Creatinine clearance (optional)

        Returns:
            Dose calculation results
        """
        drug_lower = drug_name.lower()

        # Extract numeric dose from standard_dose
        import re
        dose_match = re.search(r'(\d+(?:\.\d+)?)', standard_dose)
        if not dose_match:
            return {"error": "Could not parse standard dose"}

        standard_dose_value = float(dose_match.group(1))

        # Age-based adjustments
        adjustment_factor = 1.0

        if age > 75:
            adjustment_factor *= 0.75  # 25% reduction
        if age > 85:
            adjustment_factor *= 0.75  # Additional 25% reduction

        # Drug-specific adjustments
        drug_adjustments = {
            "digoxin": 0.5,  # 50% reduction
            "warfarin": 0.8,  # 20% reduction
            "lithium": 0.5,   # 50% reduction
            "theophylline": 0.5  # 50% reduction
        }

        if drug_lower in drug_adjustments:
            adjustment_factor *= drug_adjustments[drug_lower]

        # Renal function adjustment (if creatinine clearance provided)
        if creatinine_clearance:
            if creatinine_clearance < 30:
                adjustment_factor *= 0.5  # 50% reduction for severe renal impairment
            elif creatinine_clearance < 50:
                adjustment_factor *= 0.75  # 25% reduction for moderate renal impairment

        calculated_dose = standard_dose_value * adjustment_factor

        return {
            "drug_name": drug_name,
            "standard_dose": standard_dose,
            "calculated_dose": f"{calculated_dose:.1f} {standard_dose.replace(str(standard_dose_value), '').strip()}",
            "adjustment_factor": adjustment_factor,
            "adjustment_reasons": self._get_adjustment_reasons(age, creatinine_clearance, drug_name)
        }

    def _get_adjustment_reasons(self, age: Union[int, float], creatinine_clearance: Optional[float],
                               drug_name: str) -> List[str]:
        """Get reasons for dose adjustments."""
        reasons = []

        if age > 75:
            reasons.append("Age > 75 years")
        if age > 85:
            reasons.append("Age > 85 years")

        if creatinine_clearance:
            if creatinine_clearance < 30:
                reasons.append("Severe renal impairment")
            elif creatinine_clearance < 50:
                reasons.append("Moderate renal impairment")

        drug_lower = drug_name.lower()
        if drug_lower in self.dose_adjustment_drugs:
            reasons.append("Drug-specific Beers Criteria adjustment")

        return reasons
