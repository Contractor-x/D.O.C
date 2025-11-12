"""
Age Checker Service
Validates drug safety based on patient age using Beers Criteria and pediatric guidelines.
"""

import logging
from typing import Dict, List, Optional, Union
import json
from pathlib import Path

from .risk_scorer import RiskScorer
from .pediatric_rules import PediatricRules

logger = logging.getLogger(__name__)


class AgeChecker:
    """Service for age-based drug safety verification."""

    def __init__(self):
        self.risk_scorer = RiskScorer()
        self.pediatric_rules = PediatricRules()

        # Load Beers Criteria data
        self.beers_criteria = self._load_beers_criteria()

    def check_drug_age_safety(self, drug_name: str, dosage: str, patient_age: Union[int, float],
                             conditions: Optional[List[str]] = None) -> Dict:
        """
        Check if a drug is safe for a patient based on their age.

        Args:
            drug_name: Name of the drug
            dosage: Drug dosage (e.g., "10mg", "5ml")
            patient_age: Patient age in years
            conditions: List of patient conditions (optional)

        Returns:
            Dict containing safety assessment
        """
        try:
            assessment = {
                "drug_name": drug_name,
                "dosage": dosage,
                "patient_age": patient_age,
                "safe": True,
                "risk_level": "low",  # low, moderate, high, critical
                "warnings": [],
                "recommendations": [],
                "age_category": self._get_age_category(patient_age),
                "checked_criteria": []
            }

            # Check pediatric safety (age < 18)
            if patient_age < 18:
                pediatric_check = self.pediatric_rules.check_pediatric_safety(
                    drug_name, dosage, patient_age, conditions or []
                )
                assessment["checked_criteria"].append("pediatric")
                self._merge_assessment(assessment, pediatric_check)

            # Check Beers Criteria for all ages
            beers_check = self._check_beers_criteria(drug_name, patient_age, conditions or [])
            if beers_check:
                assessment["checked_criteria"].append("beers_criteria")
                self._merge_assessment(assessment, beers_check)

            # Calculate overall risk score
            risk_score = self.risk_scorer.calculate_risk_score(assessment)
            assessment["risk_score"] = risk_score

            # Update risk level based on score
            assessment["risk_level"] = self._score_to_risk_level(risk_score)

            # Generate recommendations
            assessment["recommendations"] = self._generate_recommendations(assessment)

            return assessment

        except Exception as e:
            logger.error(f"Age safety check failed for {drug_name}: {e}")
            return {
                "drug_name": drug_name,
                "dosage": dosage,
                "patient_age": patient_age,
                "safe": False,
                "risk_level": "unknown",
                "warnings": [f"Unable to assess safety: {str(e)}"],
                "recommendations": ["Consult healthcare provider"],
                "error": str(e)
            }

    def _get_age_category(self, age: Union[int, float]) -> str:
        """Categorize patient age."""
        if age < 2:
            return "infant"
        elif age < 12:
            return "child"
        elif age < 18:
            return "adolescent"
        else:
            return "adult"

    def _merge_assessment(self, main_assessment: Dict, check_result: Dict):
        """Merge results from different age checks."""
        if not check_result.get("safe", True):
            main_assessment["safe"] = False

        # Merge warnings
        main_assessment["warnings"].extend(check_result.get("warnings", []))

        # Update risk level if higher
        check_risk = check_result.get("risk_level", "low")
        if self._risk_level_priority(check_risk) > self._risk_level_priority(main_assessment["risk_level"]):
            main_assessment["risk_level"] = check_risk

    def _risk_level_priority(self, risk_level: str) -> int:
        """Get priority value for risk levels (higher = more severe)."""
        priorities = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
        return priorities.get(risk_level, 0)

    def _check_beers_criteria(self, drug_name: str, age: Union[int, float],
                            conditions: List[str]) -> Optional[Dict]:
        """Check drug against Beers Criteria."""
        if not self.beers_criteria:
            return None

        drug_lower = drug_name.lower()

        # Check for drugs to avoid with certain conditions
        for drug in self.beers_criteria.get("drugs_to_avoid_with_conditions", []):
            drug_name_match = drug_lower in drug.get("name", "").lower()
            condition_match = any(cond.lower() in drug.get("condition", "").lower() for cond in conditions)

            if drug_name_match and condition_match:
                return {
                    "safe": False,
                    "risk_level": "high",
                    "warnings": [f"Beers Criteria: Avoid with {drug.get('condition')} - {drug.get('reason', 'Not recommended')}"],
                    "source": "beers_criteria"
                }

        return None

    def _score_to_risk_level(self, score: float) -> str:
        """Convert risk score to risk level."""
        if score >= 8.0:
            return "critical"
        elif score >= 6.0:
            return "high"
        elif score >= 4.0:
            return "moderate"
        else:
            return "low"

    def _generate_recommendations(self, assessment: Dict) -> List[str]:
        """Generate recommendations based on assessment."""
        recommendations = []

        risk_level = assessment.get("risk_level", "low")
        age_category = assessment.get("age_category", "adult")

        if risk_level == "critical":
            recommendations.append("Immediately consult healthcare provider")
            recommendations.append("Do not take this medication without supervision")

        elif risk_level == "high":
            recommendations.append("Consult healthcare provider before taking")
            recommendations.append("Consider alternative medications")

        elif risk_level == "moderate":
            recommendations.append("Monitor for side effects closely")
            recommendations.append("Discuss with healthcare provider")

        if age_category in ["infant", "child"]:
            recommendations.append("Ensure dosage is appropriate for weight")
            recommendations.append("Consult pediatrician")

        if not assessment.get("safe", True):
            recommendations.append("Alternative medications may be available")

        return recommendations

    def _load_beers_criteria(self) -> Dict:
        """Load Beers Criteria data."""
        try:
            # In production, this would load from a JSON file
            # For now, using sample data
            return {
                "drugs_to_avoid_with_conditions": [
                    {
                        "name": "NSAIDs",
                        "condition": "heart failure",
                        "reason": "May exacerbate heart failure"
                    },
                    {
                        "name": "beta blockers",
                        "condition": "asthma",
                        "reason": "May cause bronchospasm"
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Failed to load Beers Criteria: {e}")
            return {}

    async def batch_check_safety(self, drug_list: List[Dict]) -> List[Dict]:
        """
        Check safety for multiple drugs.

        Args:
            drug_list: List of dicts with drug_name, dosage, patient_age, conditions

        Returns:
            List of safety assessments
        """
        import asyncio

        tasks = [
            self.check_drug_age_safety(
                drug["drug_name"],
                drug.get("dosage", ""),
                drug["patient_age"],
                drug.get("conditions", [])
            )
            for drug in drug_list
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch safety check failed for item {i}: {result}")
                processed_results.append({
                    "drug_name": drug_list[i].get("drug_name", "Unknown"),
                    "safe": False,
                    "risk_level": "unknown",
                    "warnings": [f"Assessment failed: {str(result)}"],
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results
