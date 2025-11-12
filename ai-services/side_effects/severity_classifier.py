"""
Severity Classifier Service
Classifies the severity of drug side effects and adverse reactions.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """Service for classifying side effect severity and managing adverse reactions."""

    def __init__(self):
        # FDA severity classification system
        self.fda_severity_levels = {
            "mild": {
                "description": "No limitation of usual activities",
                "examples": ["mild headache", "nausea", "rash"],
                "action": "Continue medication, monitor symptoms"
            },
            "moderate": {
                "description": "Some limitation of usual activities",
                "examples": ["moderate pain", "vomiting", "dizziness"],
                "action": "May need dose adjustment or symptomatic treatment"
            },
            "severe": {
                "description": "Inability to perform usual activities",
                "examples": ["severe pain", "hospitalization needed", "life-threatening"],
                "action": "Immediate medical attention required"
            },
            "life_threatening": {
                "description": "Immediate risk of death",
                "examples": ["anaphylaxis", "severe bleeding", "cardiac arrest"],
                "action": "Emergency medical care required"
            }
        }

        # Severity scoring system
        self.severity_weights = {
            "mild": 1,
            "moderate": 2,
            "severe": 3,
            "life_threatening": 4
        }

        # Critical symptoms requiring immediate action
        self.critical_symptoms = [
            "anaphylaxis", "angioedema", "severe bleeding", "cardiac arrest",
            "seizure", "coma", "respiratory distress", "severe hypotension"
        ]

    def classify_severity(self, side_effect: str, patient_context: Optional[Dict] = None) -> Dict:
        """
        Classify the severity of a side effect.

        Args:
            side_effect: Description of the side effect
            patient_context: Patient context (age, conditions, etc.)

        Returns:
            Severity classification
        """
        try:
            side_effect_lower = side_effect.lower()

            classification = {
                "side_effect": side_effect,
                "severity_level": "mild",  # default
                "severity_score": 1,
                "requires_attention": False,
                "recommended_action": "",
                "urgency": "routine",
                "monitoring_required": False
            }

            # Check for critical symptoms
            if any(critical in side_effect_lower for critical in self.critical_symptoms):
                classification.update({
                    "severity_level": "life_threatening",
                    "severity_score": 4,
                    "requires_attention": True,
                    "recommended_action": "Seek emergency medical care immediately",
                    "urgency": "emergency"
                })
                return classification

            # Check severity keywords
            severity_indicators = {
                "life_threatening": ["life-threatening", "fatal", "death", "cardiac arrest", "anaphylactic shock"],
                "severe": ["severe", "intense", "unbearable", "hospitalization", "emergency", "critical"],
                "moderate": ["moderate", "significant", "bothersome", "interfering", "limiting"],
                "mild": ["mild", "slight", "minimal", "tolerable", "manageable"]
            }

            for level, keywords in severity_indicators.items():
                if any(keyword in side_effect_lower for keyword in keywords):
                    classification["severity_level"] = level
                    classification["severity_score"] = self.severity_weights[level]
                    break

            # Adjust for patient context
            if patient_context:
                classification = self._adjust_for_context(classification, patient_context)

            # Set recommended action and urgency
            level_info = self.fda_severity_levels[classification["severity_level"]]
            classification["recommended_action"] = level_info["action"]

            if classification["severity_score"] >= 3:
                classification["requires_attention"] = True
                classification["urgency"] = "urgent"
                classification["monitoring_required"] = True
            elif classification["severity_score"] == 2:
                classification["monitoring_required"] = True
                classification["urgency"] = "soon"

            return classification

        except Exception as e:
            logger.error(f"Severity classification failed for '{side_effect}': {e}")
            return {
                "side_effect": side_effect,
                "severity_level": "unknown",
                "error": str(e)
            }

    def _adjust_for_context(self, classification: Dict, context: Dict) -> Dict:
        """Adjust severity classification based on patient context."""
        age = context.get("age")
        conditions = context.get("conditions", [])
        conditions_lower = [c.lower() for c in conditions]

        # Age adjustments
        if age and age >= 65:
            # Elderly patients may have reduced tolerance
            if classification["severity_level"] == "moderate":
                classification["severity_level"] = "severe"
                classification["severity_score"] = 3

        elif age and age < 18:
            # Children may be more vulnerable
            if classification["severity_level"] == "mild":
                classification["severity_level"] = "moderate"
                classification["severity_score"] = 2

        # Condition adjustments
        if "heart disease" in " ".join(conditions_lower):
            if "chest pain" in classification["side_effect"].lower():
                classification["severity_level"] = "life_threatening"
                classification["severity_score"] = 4

        if "diabetes" in " ".join(conditions_lower):
            if any(term in classification["side_effect"].lower() for term in ["hypoglycemia", "hyperglycemia"]):
                classification["severity_level"] = "severe"
                classification["severity_score"] = 3

        if "asthma" in " ".join(conditions_lower):
            if "breathing difficulty" in classification["side_effect"].lower():
                classification["severity_level"] = "life_threatening"
                classification["severity_score"] = 4

        return classification

    def batch_classify_severity(self, side_effects: List[str], patient_context: Optional[Dict] = None) -> List[Dict]:
        """
        Classify severity for multiple side effects.

        Args:
            side_effects: List of side effect descriptions
            patient_context: Patient context

        Returns:
            List of severity classifications
        """
        classifications = []

        for effect in side_effects:
            classification = self.classify_severity(effect, patient_context)
            classifications.append(classification)

        return classifications

    def calculate_overall_severity(self, side_effects: List[Dict]) -> Dict:
        """
        Calculate overall severity from multiple side effects.

        Args:
            side_effects: List of side effect classifications

        Returns:
            Overall severity assessment
        """
        if not side_effects:
            return {
                "overall_severity": "none",
                "highest_severity": "none",
                "severity_score": 0,
                "requires_medical_attention": False
            }

        scores = [effect.get("severity_score", 1) for effect in side_effects]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        # Determine overall severity
        if max_score >= 4:
            overall = "life_threatening"
        elif max_score >= 3:
            overall = "severe"
        elif max_score >= 2 or avg_score >= 1.5:
            overall = "moderate"
        else:
            overall = "mild"

        # Get highest severity level
        severity_levels = {4: "life_threatening", 3: "severe", 2: "moderate", 1: "mild"}
        highest_severity = severity_levels.get(max_score, "mild")

        return {
            "overall_severity": overall,
            "highest_severity": highest_severity,
            "severity_score": round(avg_score, 2),
            "max_severity_score": max_score,
            "side_effects_count": len(side_effects),
            "requires_medical_attention": max_score >= 3,
            "recommendations": self._get_overall_recommendations(overall, side_effects)
        }

    def _get_overall_recommendations(self, overall_severity: str, side_effects: List[Dict]) -> List[str]:
        """Get recommendations based on overall severity."""
        recommendations = []

        if overall_severity == "life_threatening":
            recommendations.extend([
                "Seek emergency medical care immediately",
                "Stop medication until evaluated by healthcare provider",
                "Report to emergency room or call emergency services"
            ])

        elif overall_severity == "severe":
            recommendations.extend([
                "Contact healthcare provider immediately",
                "Do not continue medication without medical advice",
                "May require hospitalization or treatment adjustment"
            ])

        elif overall_severity == "moderate":
            recommendations.extend([
                "Contact healthcare provider within 24 hours",
                "Monitor symptoms closely",
                "May need dose adjustment or additional treatment"
            ])

        else:  # mild
            recommendations.extend([
                "Continue monitoring symptoms",
                "Contact healthcare provider if symptoms worsen",
                "May continue medication with close observation"
            ])

        # Check for specific patterns
        has_critical = any(effect.get("severity_level") == "life_threatening" for effect in side_effects)
        if has_critical:
            recommendations.insert(0, "CRITICAL: Emergency medical attention required")

        return recommendations

    def get_severity_trends(self, side_effect_history: List[Dict]) -> Dict:
        """
        Analyze severity trends over time.

        Args:
            side_effect_history: List of historical side effect reports

        Returns:
            Trend analysis
        """
        if not side_effect_history:
            return {"error": "No history provided"}

        trends = {
            "total_reports": len(side_effect_history),
            "severity_progression": [],
            "worsening_trend": False,
            "improvement_trend": False,
            "stable": True,
            "recommendations": []
        }

        # Sort by date (assuming chronological order)
        sorted_history = sorted(side_effect_history, key=lambda x: x.get("date", ""))

        previous_score = None
        for i, report in enumerate(sorted_history):
            current_score = report.get("severity_score", 1)
            trends["severity_progression"].append({
                "date": report.get("date", f"Report {i+1}"),
                "severity": report.get("severity_level", "unknown"),
                "score": current_score
            })

            if previous_score is not None:
                if current_score > previous_score:
                    trends["worsening_trend"] = True
                    trends["stable"] = False
                elif current_score < previous_score:
                    trends["improvement_trend"] = True
                    trends["stable"] = False

            previous_score = current_score

        # Generate trend-based recommendations
        if trends["worsening_trend"]:
            trends["recommendations"].append("Side effects are worsening - immediate medical evaluation required")
            trends["recommendations"].append("Consider medication discontinuation or dose reduction")

        elif trends["improvement_trend"]:
            trends["recommendations"].append("Side effects are improving - continue monitoring")
            trends["recommendations"].append("May be able to continue medication with close supervision")

        else:
            trends["recommendations"].append("Side effects are stable - continue current management")

        return trends

    def assess_adverse_reaction(self, reaction_description: str, drug_name: str,
                              patient_profile: Dict) -> Dict:
        """
        Assess an adverse drug reaction comprehensively.

        Args:
            reaction_description: Description of the adverse reaction
            drug_name: Name of the drug involved
            patient_profile: Patient profile information

        Returns:
            Comprehensive adverse reaction assessment
        """
        try:
            # Classify the reaction
            severity = self.classify_severity(reaction_description, patient_profile)

            assessment = {
                "drug_name": drug_name,
                "reaction_description": reaction_description,
                "severity_assessment": severity,
                "patient_profile": patient_profile,
                "is_adverse_reaction": True,
                "reporting_required": False,
                "risk_assessment": {},
                "management_plan": []
            }

            # Determine if reporting is required (FDA criteria)
            assessment["reporting_required"] = self._requires_fda_reporting(severity, reaction_description)

            # Risk assessment
            assessment["risk_assessment"] = self._assess_reaction_risk(
                severity, drug_name, patient_profile
            )

            # Management plan
            assessment["management_plan"] = self._create_management_plan(
                severity, reaction_description, patient_profile
            )

            return assessment

        except Exception as e:
            logger.error(f"Adverse reaction assessment failed: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e),
                "is_adverse_reaction": False
            }

    def _requires_fda_reporting(self, severity: Dict, description: str) -> bool:
        """Determine if adverse reaction requires FDA reporting."""
        # FDA requires reporting of serious adverse events
        if severity.get("severity_level") in ["severe", "life_threatening"]:
            return True

        # Check for specific reportable events
        reportable_terms = [
            "death", "hospitalization", "disability", "congenital anomaly",
            "cancer", "overdose", "medication error"
        ]

        description_lower = description.lower()
        return any(term in description_lower for term in reportable_terms)

    def _assess_reaction_risk(self, severity: Dict, drug_name: str, patient_profile: Dict) -> Dict:
        """Assess risk factors for the adverse reaction."""
        risk_factors = []
        risk_score = 0

        # Severity-based risk
        severity_score = severity.get("severity_score", 1)
        risk_score += severity_score

        if severity_score >= 3:
            risk_factors.append("High severity reaction")

        # Patient factors
        age = patient_profile.get("age")
        if age and age >= 65:
            risk_score += 1
            risk_factors.append("Elderly patient")

        conditions = patient_profile.get("conditions", [])
        if conditions:
            risk_score += len(conditions) * 0.5
            risk_factors.append(f"Multiple conditions: {len(conditions)}")

        # Drug factors (simplified)
        high_risk_drugs = ["warfarin", "insulin", "chemotherapy"]
        if drug_name.lower() in high_risk_drugs:
            risk_score += 1
            risk_factors.append("High-risk medication")

        return {
            "risk_score": round(risk_score, 1),
            "risk_level": "high" if risk_score >= 3 else "moderate" if risk_score >= 2 else "low",
            "risk_factors": risk_factors
        }

    def _create_management_plan(self, severity: Dict, description: str, patient_profile: Dict) -> List[str]:
        """Create a management plan for the adverse reaction."""
        plan = []

        severity_level = severity.get("severity_level")

        if severity_level == "life_threatening":
            plan.extend([
                "Immediate discontinuation of medication",
                "Emergency medical evaluation",
                "Supportive care as needed",
                "Monitor vital signs continuously"
            ])

        elif severity_level == "severe":
            plan.extend([
                "Discontinue medication immediately",
                "Seek medical evaluation within hours",
                "Symptomatic treatment",
                "Close monitoring for 24-48 hours"
            ])

        elif severity_level == "moderate":
            plan.extend([
                "Consider dose reduction or discontinuation",
                "Medical evaluation within 24 hours",
                "Symptomatic treatment",
                "Regular monitoring"
            ])

        else:  # mild
            plan.extend([
                "Continue monitoring symptoms",
                "Medical evaluation if symptoms persist or worsen",
                "Consider symptomatic treatment"
            ])

        # Add specific management based on reaction type
        description_lower = description.lower()

        if "rash" in description_lower or "allergic" in description_lower:
            plan.append("Antihistamine treatment if appropriate")
            plan.append("Avoid future exposure to similar medications")

        if "nausea" in description_lower or "vomiting" in description_lower:
            plan.append("Antiemetic treatment as needed")

        if "pain" in description_lower:
            plan.append("Pain management with appropriate analgesics")

        return plan
