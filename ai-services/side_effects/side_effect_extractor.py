"""
Side Effect Extractor Service
Extracts and analyzes drug side effects from various sources.
"""

import logging
from typing import Dict, List, Optional, Union
import re

logger = logging.getLogger(__name__)


class SideEffectExtractor:
    """Service for extracting and analyzing drug side effects."""

    def __init__(self):
        # Common side effects database (in production, this would be from a comprehensive database)
        self.side_effects_db = {
            "acetaminophen": {
                "common": ["nausea", "rash", "headache"],
                "rare": ["liver toxicity", "anaphylaxis"],
                "frequency": {"nausea": 0.05, "rash": 0.02, "headache": 0.03}
            },
            "ibuprofen": {
                "common": ["stomach upset", "heartburn", "dizziness"],
                "rare": ["gastric ulcer", "kidney damage", "heart attack"],
                "frequency": {"stomach upset": 0.15, "heartburn": 0.10, "dizziness": 0.05}
            },
            "amoxicillin": {
                "common": ["diarrhea", "nausea", "rash"],
                "rare": ["severe allergic reaction", "pseudomembranous colitis"],
                "frequency": {"diarrhea": 0.08, "nausea": 0.06, "rash": 0.05}
            },
            "lisinopril": {
                "common": ["cough", "dizziness", "headache"],
                "rare": ["angioedema", "hyperkalemia", "acute kidney injury"],
                "frequency": {"cough": 0.10, "dizziness": 0.08, "headache": 0.06}
            },
            "metoprolol": {
                "common": ["fatigue", "dizziness", "slow heart rate"],
                "rare": ["heart block", "worsening heart failure"],
                "frequency": {"fatigue": 0.12, "dizziness": 0.08, "slow heart rate": 0.05}
            },
            "warfarin": {
                "common": ["bruising", "bleeding"],
                "rare": ["severe bleeding", "skin necrosis"],
                "frequency": {"bruising": 0.20, "bleeding": 0.15}
            }
        }

        # Side effect severity levels
        self.severity_levels = {
            "mild": ["nausea", "headache", "dizziness", "fatigue", "rash"],
            "moderate": ["vomiting", "diarrhea", "cough", "bruising", "heartburn"],
            "severe": ["anaphylaxis", "angioedema", "gastric ulcer", "kidney damage", "heart attack"],
            "life_threatening": ["severe bleeding", "liver toxicity", "heart block"]
        }

    def extract_side_effects(self, drug_name: str, patient_age: Optional[Union[int, float]] = None,
                           conditions: Optional[List[str]] = None) -> Dict:
        """
        Extract side effects for a drug based on patient factors.

        Args:
            drug_name: Name of the drug
            patient_age: Patient age (optional)
            conditions: Patient conditions (optional)

        Returns:
            Side effects analysis
        """
        try:
            drug_lower = drug_name.lower()

            analysis = {
                "drug_name": drug_name,
                "common_side_effects": [],
                "rare_side_effects": [],
                "age_related_effects": [],
                "condition_related_effects": [],
                "severity_distribution": {},
                "recommendations": []
            }

            # Get base side effects
            if drug_lower in self.side_effects_db:
                drug_data = self.side_effects_db[drug_lower]
                analysis["common_side_effects"] = drug_data.get("common", [])
                analysis["rare_side_effects"] = drug_data.get("rare", [])

            # Age-related side effects
            if patient_age is not None:
                age_effects = self._get_age_related_effects(drug_lower, patient_age)
                analysis["age_related_effects"] = age_effects

            # Condition-related side effects
            if conditions:
                condition_effects = self._get_condition_related_effects(drug_lower, conditions)
                analysis["condition_related_effects"] = condition_effects

            # Calculate severity distribution
            all_effects = (analysis["common_side_effects"] +
                          analysis["rare_side_effects"] +
                          analysis["age_related_effects"] +
                          analysis["condition_related_effects"])

            analysis["severity_distribution"] = self._calculate_severity_distribution(all_effects)

            # Generate recommendations
            analysis["recommendations"] = self._generate_side_effect_recommendations(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Side effect extraction failed for {drug_name}: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e),
                "common_side_effects": [],
                "recommendations": ["Consult healthcare provider for side effect information"]
            }

    def _get_age_related_effects(self, drug_name: str, age: Union[int, float]) -> List[str]:
        """Get age-related side effects."""
        effects = []

        if age >= 65:
            # Geriatric-specific side effects
            if drug_name == "ibuprofen":
                effects.extend(["increased bleeding risk", "gastric irritation"])
            elif drug_name == "lisinopril":
                effects.extend(["orthostatic hypotension", "hyperkalemia"])
            elif drug_name == "metoprolol":
                effects.extend(["bradycardia", "fatigue"])

        elif age < 18:
            # Pediatric-specific side effects
            if drug_name == "tetracycline":
                effects.append("tooth discoloration")
            elif drug_name == "fluoroquinolones":
                effects.append("cartilage damage")

        return effects

    def _get_condition_related_effects(self, drug_name: str, conditions: List[str]) -> List[str]:
        """Get condition-related side effects."""
        effects = []
        conditions_lower = [c.lower() for c in conditions]

        # Heart failure
        if "heart failure" in " ".join(conditions_lower):
            if drug_name in ["ibuprofen", "naproxen"]:
                effects.append("fluid retention")
                effects.append("worsening heart failure")

        # Kidney disease
        if any(c in ["kidney disease", "renal impairment", "ckd"] for c in conditions_lower):
            if drug_name in ["ibuprofen", "lisinopril"]:
                effects.append("acute kidney injury")
                effects.append("hyperkalemia")

        # Asthma
        if "asthma" in conditions_lower:
            if drug_name in ["aspirin", "ibuprofen", "beta blockers"]:
                effects.append("bronchospasm")

        # Diabetes
        if "diabetes" in conditions_lower:
            if drug_name == "beta blockers":
                effects.append("masking of hypoglycemia symptoms")

        return effects

    def _calculate_severity_distribution(self, effects: List[str]) -> Dict:
        """Calculate severity distribution of side effects."""
        distribution = {"mild": 0, "moderate": 0, "severe": 0, "life_threatening": 0}

        for effect in effects:
            effect_lower = effect.lower()
            severity = "mild"  # default

            for level, symptoms in self.severity_levels.items():
                if any(symptom in effect_lower for symptom in symptoms):
                    severity = level
                    break

            distribution[severity] += 1

        return distribution

    def _generate_side_effect_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on side effects analysis."""
        recommendations = []

        severity_dist = analysis.get("severity_distribution", {})

        # General recommendations
        if analysis["common_side_effects"]:
            recommendations.append("Monitor for common side effects and report if severe")

        # Severity-based recommendations
        if severity_dist.get("severe", 0) > 0 or severity_dist.get("life_threatening", 0) > 0:
            recommendations.append("Close monitoring required for severe side effects")
            recommendations.append("Report any severe symptoms immediately")

        # Age-specific recommendations
        if analysis["age_related_effects"]:
            recommendations.append("Extra vigilance needed for age-related side effects")

        # Condition-specific recommendations
        if analysis["condition_related_effects"]:
            recommendations.append("Monitor closely due to underlying conditions")

        # Drug-specific recommendations
        drug_lower = analysis["drug_name"].lower()
        if drug_lower == "warfarin":
            recommendations.append("Regular INR monitoring required")
        elif drug_lower in ["lisinopril", "metoprolol"]:
            recommendations.append("Monitor blood pressure and heart rate")

        return recommendations

    def predict_side_effect_risk(self, drug_name: str, patient_profile: Dict) -> Dict:
        """
        Predict side effect risk based on patient profile.

        Args:
            drug_name: Name of the drug
            patient_profile: Patient profile dictionary

        Returns:
            Risk prediction
        """
        try:
            base_risk = "low"
            risk_factors = []
            risk_score = 0

            drug_lower = drug_name.lower()

            # Age risk factors
            age = patient_profile.get("age")
            if age and age >= 65:
                risk_score += 2
                risk_factors.append("Age ≥65 years")
                base_risk = "moderate"

            # Weight risk factors
            weight = patient_profile.get("weight_kg")
            if weight and weight < 50:
                risk_score += 1
                risk_factors.append("Low body weight")

            # Conditions risk factors
            conditions = patient_profile.get("conditions", [])
            conditions_lower = [c.lower() for c in conditions]

            if "heart failure" in " ".join(conditions_lower):
                risk_score += 2
                risk_factors.append("Heart failure")

            if "kidney disease" in " ".join(conditions_lower):
                risk_score += 2
                risk_factors.append("Kidney disease")

            if "liver disease" in " ".join(conditions_lower):
                risk_score += 2
                risk_factors.append("Liver disease")

            # Gender risk factors
            gender = patient_profile.get("gender", "").lower()
            if gender == "female" and drug_lower in ["warfarin", "lithium"]:
                risk_score += 1
                risk_factors.append("Gender-specific risk")

            # Calculate final risk level
            if risk_score >= 4:
                final_risk = "high"
            elif risk_score >= 2:
                final_risk = "moderate"
            else:
                final_risk = "low"

            return {
                "drug_name": drug_name,
                "predicted_risk": final_risk,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "recommendations": self._get_risk_based_recommendations(final_risk, drug_name)
            }

        except Exception as e:
            logger.error(f"Side effect risk prediction failed for {drug_name}: {e}")
            return {
                "drug_name": drug_name,
                "predicted_risk": "unknown",
                "error": str(e)
            }

    def _get_risk_based_recommendations(self, risk_level: str, drug_name: str) -> List[str]:
        """Get recommendations based on risk level."""
        recommendations = []

        if risk_level == "high":
            recommendations.extend([
                "Close monitoring required",
                "Consider alternative medications",
                "Report any new symptoms immediately"
            ])

        elif risk_level == "moderate":
            recommendations.extend([
                "Regular monitoring advised",
                "Discuss benefits vs risks with healthcare provider"
            ])

        else:  # low
            recommendations.append("Routine monitoring for side effects")

        # Drug-specific recommendations
        drug_lower = drug_name.lower()
        if drug_lower == "warfarin":
            recommendations.append("Regular INR monitoring essential")
        elif drug_lower in ["lisinopril", "metoprolol"]:
            recommendations.append("Monitor blood pressure and electrolytes")

        return recommendations

    def analyze_side_effect_text(self, text: str) -> Dict:
        """
        Analyze text for side effect mentions.

        Args:
            text: Text containing potential side effect descriptions

        Returns:
            Analysis of side effects mentioned in text
        """
        try:
            text_lower = text.lower()

            found_effects = []
            severity_assessment = {"mild": 0, "moderate": 0, "severe": 0, "life_threatening": 0}

            # Check for each known side effect
            for drug, data in self.side_effects_db.items():
                for category in ["common", "rare"]:
                    for effect in data.get(category, []):
                        if effect.lower() in text_lower:
                            found_effects.append({
                                "effect": effect,
                                "drug": drug,
                                "category": category
                            })

                            # Assess severity
                            effect_lower = effect.lower()
                            for level, symptoms in self.severity_levels.items():
                                if any(symptom in effect_lower for symptom in symptoms):
                                    severity_assessment[level] += 1
                                    break

            return {
                "found_side_effects": found_effects,
                "severity_assessment": severity_assessment,
                "total_mentions": len(found_effects),
                "requires_attention": severity_assessment["severe"] + severity_assessment["life_threatening"] > 0
            }

        except Exception as e:
            logger.error(f"Side effect text analysis failed: {e}")
            return {
                "error": str(e),
                "found_side_effects": [],
                "severity_assessment": {}
            }
