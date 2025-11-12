"""
Interaction Checker Service
Checks for drug-drug and drug-disease interactions.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class InteractionChecker:
    """Service for checking drug interactions and contraindications."""

    def __init__(self):
        # Drug interaction database (simplified for demonstration)
        self.drug_interactions = {
            "warfarin": {
                "interacts_with": ["aspirin", "ibuprofen", "amiodarone", "fluconazole"],
                "severity": {
                    "aspirin": "major",
                    "ibuprofen": "moderate",
                    "amiodarone": "major",
                    "fluconazole": "major"
                },
                "effects": {
                    "aspirin": "Increased bleeding risk",
                    "ibuprofen": "Increased bleeding risk",
                    "amiodarone": "Increased warfarin effect",
                    "fluconazole": "Increased warfarin effect"
                }
            },
            "lisinopril": {
                "interacts_with": ["potassium_supplements", "spironolactone", "ibuprofen"],
                "severity": {
                    "potassium_supplements": "major",
                    "spironolactone": "major",
                    "ibuprofen": "moderate"
                },
                "effects": {
                    "potassium_supplements": "Hyperkalemia",
                    "spironolactone": "Hyperkalemia, renal impairment",
                    "ibuprofen": "Reduced antihypertensive effect"
                }
            },
            "metoprolol": {
                "interacts_with": ["verapamil", "diltiazem", "amiodarone"],
                "severity": {
                    "verapamil": "major",
                    "diltiazem": "moderate",
                    "amiodarone": "moderate"
                },
                "effects": {
                    "verapamil": "Bradycardia, heart block",
                    "diltiazem": "Bradycardia, heart block",
                    "amiodarone": "Bradycardia, increased beta-blocker effect"
                }
            },
            "amoxicillin": {
                "interacts_with": ["warfarin", "oral_contraceptives"],
                "severity": {
                    "warfarin": "moderate",
                    "oral_contraceptives": "minor"
                },
                "effects": {
                    "warfarin": "May alter warfarin effect",
                    "oral_contraceptives": "Reduced contraceptive effectiveness"
                }
            }
        }

        # Disease-drug contraindications
        self.disease_contraindications = {
            "heart_failure": ["ibuprofen", "naproxen", "pioglitazone"],
            "kidney_disease": ["ibuprofen", "naproxen", "lisinopril"],
            "liver_disease": ["acetaminophen", "ibuprofen", "methotrexate"],
            "asthma": ["aspirin", "ibuprofen", "beta_blockers"],
            "diabetes": ["thiazide_diuretics", "beta_blockers"],
            "gout": ["aspirin", "niacin", "thiazide_diuretics"]
        }

        # Interaction severity levels
        self.severity_levels = {
            "minor": {"description": "Little clinical significance", "action": "Monitor therapy"},
            "moderate": {"description": "May require dose adjustment", "action": "Monitor closely, consider alternatives"},
            "major": {"description": "Potentially life-threatening", "action": "Avoid combination or adjust therapy"}
        }

    def check_drug_interactions(self, drug_list: List[str], patient_conditions: Optional[List[str]] = None) -> Dict:
        """
        Check for interactions between drugs and with patient conditions.

        Args:
            drug_list: List of drug names
            patient_conditions: List of patient conditions

        Returns:
            Interaction analysis
        """
        try:
            analysis = {
                "drugs_checked": drug_list,
                "drug_drug_interactions": [],
                "drug_disease_interactions": [],
                "total_interactions": 0,
                "severity_summary": {"minor": 0, "moderate": 0, "major": 0},
                "recommendations": [],
                "requires_attention": False
            }

            # Check drug-drug interactions
            drug_interactions = self._check_drug_drug_interactions(drug_list)
            analysis["drug_drug_interactions"] = drug_interactions

            # Check drug-disease interactions
            disease_interactions = []
            if patient_conditions:
                disease_interactions = self._check_drug_disease_interactions(drug_list, patient_conditions)
                analysis["drug_disease_interactions"] = disease_interactions

            # Calculate totals and severity
            all_interactions = drug_interactions + disease_interactions
            analysis["total_interactions"] = len(all_interactions)

            for interaction in all_interactions:
                severity = interaction.get("severity", "minor")
                analysis["severity_summary"][severity] += 1

            # Determine if attention is required
            analysis["requires_attention"] = analysis["severity_summary"]["major"] > 0 or analysis["severity_summary"]["moderate"] > 2

            # Generate recommendations
            analysis["recommendations"] = self._generate_interaction_recommendations(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Drug interaction check failed: {e}")
            return {
                "error": str(e),
                "drugs_checked": drug_list,
                "drug_drug_interactions": [],
                "drug_disease_interactions": []
            }

    def _check_drug_drug_interactions(self, drug_list: List[str]) -> List[Dict]:
        """Check for interactions between drugs in the list."""
        interactions = []
        drug_list_lower = [d.lower() for d in drug_list]

        for i, drug1 in enumerate(drug_list):
            drug1_lower = drug1.lower()

            if drug1_lower in self.drug_interactions:
                drug1_data = self.drug_interactions[drug1_lower]

                for drug2 in drug_list[i+1:]:
                    drug2_lower = drug2.lower()

                    if drug2_lower in drug1_data["interacts_with"]:
                        interaction = {
                            "drug1": drug1,
                            "drug2": drug2,
                            "severity": drug1_data["severity"].get(drug2_lower, "moderate"),
                            "effect": drug1_data["effects"].get(drug2_lower, "Interaction detected"),
                            "type": "drug_drug",
                            "recommendation": self._get_interaction_recommendation(
                                drug1_data["severity"].get(drug2_lower, "moderate")
                            )
                        }
                        interactions.append(interaction)

        return interactions

    def _check_drug_disease_interactions(self, drug_list: List[str], conditions: List[str]) -> List[Dict]:
        """Check for interactions between drugs and patient conditions."""
        interactions = []
        conditions_normalized = [c.lower().replace(' ', '_') for c in conditions]

        for drug in drug_list:
            drug_lower = drug.lower()

            for condition, contraindicated_drugs in self.disease_contraindications.items():
                if condition in conditions_normalized:
                    if drug_lower in contraindicated_drugs:
                        interaction = {
                            "drug": drug,
                            "condition": condition,
                            "severity": "major",  # Disease contraindications are typically major
                            "effect": f"May worsen {condition.replace('_', ' ')}",
                            "type": "drug_disease",
                            "recommendation": f"Avoid {drug} in patients with {condition.replace('_', ' ')} or use with extreme caution"
                        }
                        interactions.append(interaction)

        return interactions

    def _get_interaction_recommendation(self, severity: str) -> str:
        """Get recommendation based on interaction severity."""
        return self.severity_levels.get(severity, {}).get("action", "Monitor therapy")

    def _generate_interaction_recommendations(self, analysis: Dict) -> List[str]:
        """Generate overall recommendations based on interaction analysis."""
        recommendations = []

        severity_summary = analysis.get("severity_summary", {})

        if severity_summary.get("major", 0) > 0:
            recommendations.append("Major interactions detected - avoid combinations or adjust therapy")
            recommendations.append("Consult pharmacist or physician immediately")

        if severity_summary.get("moderate", 0) > 0:
            recommendations.append("Moderate interactions present - monitor closely for adverse effects")
            recommendations.append("Consider dose adjustments or alternative medications")

        if severity_summary.get("minor", 0) > 0:
            recommendations.append("Minor interactions noted - monitor therapy")

        if analysis.get("total_interactions", 0) > 3:
            recommendations.append("Multiple interactions detected - comprehensive medication review recommended")

        if not analysis.get("requires_attention", False):
            recommendations.append("No significant interactions detected - continue monitoring")

        return recommendations

    def get_interaction_details(self, drug1: str, drug2: str) -> Dict:
        """
        Get detailed information about a specific drug-drug interaction.

        Args:
            drug1: First drug name
            drug2: Second drug name

        Returns:
            Detailed interaction information
        """
        drug1_lower = drug1.lower()
        drug2_lower = drug2.lower()

        # Check both directions (interactions are often listed unidirectionally)
        for primary_drug, data in self.drug_interactions.items():
            if primary_drug == drug1_lower and drug2_lower in data["interacts_with"]:
                return {
                    "drug1": drug1,
                    "drug2": drug2,
                    "severity": data["severity"].get(drug2_lower, "moderate"),
                    "effect": data["effects"].get(drug2_lower, "Interaction detected"),
                    "mechanism": self._get_interaction_mechanism(drug1_lower, drug2_lower),
                    "management": self._get_interaction_management(drug1_lower, drug2_lower),
                    "monitoring": self._get_monitoring_requirements(drug1_lower, drug2_lower)
                }
            elif primary_drug == drug2_lower and drug1_lower in data["interacts_with"]:
                return {
                    "drug1": drug2,
                    "drug2": drug1,
                    "severity": data["severity"].get(drug1_lower, "moderate"),
                    "effect": data["effects"].get(drug1_lower, "Interaction detected"),
                    "mechanism": self._get_interaction_mechanism(drug2_lower, drug1_lower),
                    "management": self._get_interaction_management(drug2_lower, drug1_lower),
                    "monitoring": self._get_monitoring_requirements(drug2_lower, drug1_lower)
                }

        return {
            "drug1": drug1,
            "drug2": drug2,
            "severity": "unknown",
            "effect": "No known interaction",
            "mechanism": "Not available",
            "management": "No specific management required",
            "monitoring": "Routine monitoring"
        }

    def _get_interaction_mechanism(self, drug1: str, drug2: str) -> str:
        """Get the mechanism of interaction (simplified)."""
        mechanisms = {
            ("warfarin", "aspirin"): "Both drugs affect platelet function and coagulation",
            ("warfarin", "amiodarone"): "Amiodarone inhibits warfarin metabolism",
            ("lisinopril", "potassium_supplements"): "Both increase potassium levels",
            ("metoprolol", "verapamil"): "Both slow heart rate and conduction"
        }

        return mechanisms.get((drug1, drug2), mechanisms.get((drug2, drug1), "Mechanism not fully understood"))

    def _get_interaction_management(self, drug1: str, drug2: str) -> str:
        """Get management strategies for the interaction."""
        management = {
            ("warfarin", "aspirin"): "Use lowest effective doses, monitor INR closely",
            ("warfarin", "amiodarone"): "Reduce warfarin dose by 25-50%, monitor INR",
            ("lisinopril", "potassium_supplements"): "Monitor potassium levels, consider alternatives",
            ("metoprolol", "verapamil"): "Monitor heart rate, consider dose reduction"
        }

        return management.get((drug1, drug2), management.get((drug2, drug1), "Monitor for adverse effects"))

    def _get_monitoring_requirements(self, drug1: str, drug2: str) -> str:
        """Get monitoring requirements for the interaction."""
        monitoring = {
            ("warfarin", "aspirin"): "INR every 1-2 weeks, signs of bleeding",
            ("warfarin", "amiodarone"): "INR weekly initially, then every 2 weeks",
            ("lisinopril", "potassium_supplements"): "Potassium levels every 1-2 weeks",
            ("metoprolol", "verapamil"): "Heart rate, blood pressure, ECG as needed"
        }

        return monitoring.get((drug1, drug2), monitoring.get((drug2, drug1), "Monitor for drug effects and adverse reactions"))

    def check_contraindications(self, drug: str, patient_profile: Dict) -> Dict:
        """
        Check for contraindications based on patient profile.

        Args:
            drug: Drug name
            patient_profile: Patient profile with conditions, allergies, etc.

        Returns:
            Contraindication assessment
        """
        try:
            drug_lower = drug.lower()

            assessment = {
                "drug": drug,
                "contraindications": [],
                "warnings": [],
                "safe_to_use": True,
                "severity": "none"
            }

            # Check allergies
            allergies = patient_profile.get("allergies", [])
            allergies_lower = [a.lower() for a in allergies]

            # Check for direct drug allergies
            if any(allergy in drug_lower for allergy in allergies_lower):
                assessment["contraindications"].append("Drug allergy")
                assessment["safe_to_use"] = False
                assessment["severity"] = "major"

            # Check for drug class allergies (e.g., penicillin allergy with amoxicillin)
            drug_classes = {
                "penicillin": ["amoxicillin", "penicillin", "ampicillin", "piperacillin", "amoxicillin-clavulanate"],
                "sulfa": ["sulfamethoxazole", "trimethoprim-sulfamethoxazole", "sulfasalazine"],
                "nsaid": ["ibuprofen", "naproxen", "aspirin", "diclofenac"]
            }

            for allergy in allergies_lower:
                for drug_class, drugs_in_class in drug_classes.items():
                    if allergy == drug_class and drug_lower in drugs_in_class:
                        assessment["contraindications"].append(f"{drug_class.title()} allergy - {drug} is a {drug_class}-based medication")
                        assessment["safe_to_use"] = False
                        assessment["severity"] = "major"
                        break

            # Check conditions
            conditions = patient_profile.get("conditions", [])
            conditions_lower = [c.lower() for c in conditions]

            for condition in conditions_lower:
                if condition in self.disease_contraindications:
                    contraindicated_drugs = self.disease_contraindications[condition]
                    if drug_lower in contraindicated_drugs:
                        assessment["contraindications"].append(f"Contraindicated in {condition.replace('_', ' ')}")
                        assessment["safe_to_use"] = False
                        assessment["severity"] = "major"

            # Check age
            age = patient_profile.get("age")
            if age is not None:
                age_warnings = self._check_age_contraindications(drug_lower, age)
                assessment["warnings"].extend(age_warnings)

            # Check pregnancy/lactation
            pregnancy_status = patient_profile.get("pregnancy_status")
            if pregnancy_status:
                pregnancy_warnings = self._check_pregnancy_contraindications(drug_lower, pregnancy_status)
                assessment["warnings"].extend(pregnancy_warnings)

            return assessment

        except Exception as e:
            logger.error(f"Contraindication check failed for {drug}: {e}")
            return {
                "drug": drug,
                "error": str(e),
                "safe_to_use": False
            }

    def _check_age_contraindications(self, drug: str, age: Union[int, float]) -> List[str]:
        """Check for age-related contraindications."""
        warnings = []

        if age < 18:
            if drug == "tetracycline":
                warnings.append("Contraindicated in children under 8 years (teeth discoloration)")
            elif drug == "fluoroquinolones":
                warnings.append("Not recommended in children (cartilage damage risk)")

        elif age >= 65:
            if drug in ["amitriptyline", "diphenhydramine"]:
                warnings.append("Strong anticholinergic effects may cause confusion in elderly")

        return warnings

    def _check_pregnancy_contraindications(self, drug: str, pregnancy_status: str) -> List[str]:
        """Check for pregnancy-related contraindications."""
        warnings = []

        # Simplified pregnancy categories (FDA categories)
        pregnancy_warnings = {
            "warfarin": "Category X - Contraindicated in pregnancy",
            "lisinopril": "Category C/D - Use with caution",
            "metoprolol": "Category C - Use with caution"
        }

        if drug in pregnancy_warnings:
            warnings.append(pregnancy_warnings[drug])

        return warnings

    def get_alternative_medications(self, drug: str, interaction_drug: str) -> List[Dict]:
        """
        Suggest alternative medications when interactions are present.

        Args:
            drug: Original drug
            interaction_drug: Drug causing interaction

        Returns:
            List of alternative medication suggestions
        """
        alternatives = []

        # Simplified alternative suggestions
        alternative_suggestions = {
            ("warfarin", "aspirin"): [
                {"alternative": "clopidogrel", "reason": "Alternative antiplatelet with less interaction"},
                {"alternative": "low-dose aspirin only if necessary", "reason": "Minimize aspirin dose"}
            ],
            ("lisinopril", "potassium_supplements"): [
                {"alternative": "losartan", "reason": "ARB with less hyperkalemia risk"},
                {"alternative": "amlodipine", "reason": "Calcium channel blocker alternative"}
            ],
            ("metoprolol", "verapamil"): [
                {"alternative": "diltiazem", "reason": "Alternative calcium channel blocker"},
                {"alternative": "atenolol", "reason": "Alternative beta-blocker with less interaction"}
            ]
        }

        key = (drug.lower(), interaction_drug.lower())
        reverse_key = (interaction_drug.lower(), drug.lower())

        suggestions = alternative_suggestions.get(key, alternative_suggestions.get(reverse_key, []))
        return suggestions
