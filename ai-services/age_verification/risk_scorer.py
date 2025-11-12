"""
Risk Scorer for Age Verification
Calculates risk scores for drug-age combinations.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class RiskScorer:
    """Service for calculating drug safety risk scores."""

    def __init__(self):
        # Risk weights for different factors
        self.risk_weights = {
            "age_violation": 3.0,  # Major violation of age guidelines
            "beers_criteria": 2.5,  # Beers Criteria violation
            "condition_conflict": 2.0,  # Drug conflicts with patient condition
            "high_dosage": 1.5,  # Dosage above recommended
            "interaction_risk": 1.5,  # Potential drug interactions
            "monitoring_required": 1.0,  # Requires close monitoring
            "caution_advised": 0.5,  # General caution advised
        }

    def calculate_risk_score(self, assessment: Dict) -> float:
        """
        Calculate overall risk score for a drug assessment.

        Args:
            assessment: Drug safety assessment dictionary

        Returns:
            Risk score (0-10 scale)
        """
        score = 0.0
        factors_applied = []

        # Base score from risk level
        risk_level = assessment.get("risk_level", "low")
        base_scores = {
            "low": 1.0,
            "moderate": 3.0,
            "high": 6.0,
            "critical": 9.0
        }
        score += base_scores.get(risk_level, 1.0)
        factors_applied.append(f"base_risk_{risk_level}")

        # Age category adjustments
        age_category = assessment.get("age_category", "adult")
        age_adjustments = {
            "infant": 2.0,  # Higher risk for infants
            "child": 1.5,   # Higher risk for children
            "adolescent": 1.0,  # Moderate risk for adolescents
            "adult": 0.0,   # Baseline for adults
            "geriatric": 1.5,  # Higher risk for elderly
        }
        age_adjust = age_adjustments.get(age_category, 0.0)
        score += age_adjust
        if age_adjust > 0:
            factors_applied.append(f"age_category_{age_category}")

        # Warning-based scoring
        warnings = assessment.get("warnings", [])
        for warning in warnings:
            warning_lower = warning.lower()

            if any(term in warning_lower for term in ["avoid", "contraindicated", "not recommended"]):
                score += self.risk_weights["age_violation"]
                factors_applied.append("age_violation")

            elif "beers criteria" in warning_lower:
                score += self.risk_weights["beers_criteria"]
                factors_applied.append("beers_criteria")

            elif any(term in warning_lower for term in ["heart failure", "kidney disease", "liver disease"]):
                score += self.risk_weights["condition_conflict"]
                factors_applied.append("condition_conflict")

            elif any(term in warning_lower for term in ["high dose", "maximum dose", "overdose"]):
                score += self.risk_weights["high_dosage"]
                factors_applied.append("high_dosage")

            elif "interaction" in warning_lower:
                score += self.risk_weights["interaction_risk"]
                factors_applied.append("interaction_risk")

            elif any(term in warning_lower for term in ["monitor", "watch", "observe"]):
                score += self.risk_weights["monitoring_required"]
                factors_applied.append("monitoring_required")

            elif any(term in warning_lower for term in ["caution", "careful", "aware"]):
                score += self.risk_weights["caution_advised"]
                factors_applied.append("caution_advised")

        # Criteria checked bonus/malus
        checked_criteria = assessment.get("checked_criteria", [])
        if "pediatric" in checked_criteria or "geriatric" in checked_criteria:
            score += 0.5  # Bonus for comprehensive checking
            factors_applied.append("comprehensive_check")

        # Safety flag adjustment
        if not assessment.get("safe", True):
            score += 1.0  # Additional penalty for unsafe drugs
            factors_applied.append("safety_flag")

        # Clamp score to 0-10 range
        final_score = max(0.0, min(10.0, score))

        logger.debug(f"Risk score calculation: {final_score} (factors: {factors_applied})")

        return round(final_score, 2)

    def get_risk_factors(self, assessment: Dict) -> List[Dict]:
        """
        Extract and detail risk factors from assessment.

        Args:
            assessment: Drug safety assessment

        Returns:
            List of risk factor dictionaries
        """
        factors = []

        warnings = assessment.get("warnings", [])
        for warning in warnings:
            factor = {
                "description": warning,
                "severity": self._classify_warning_severity(warning),
                "category": self._categorize_warning(warning)
            }
            factors.append(factor)

        # Add age-related factors
        age_category = assessment.get("age_category", "adult")
        if age_category in ["infant", "child", "geriatric"]:
            factors.append({
                "description": f"Special considerations for {age_category} patients",
                "severity": "moderate",
                "category": "age_related"
            })

        return factors

    def _classify_warning_severity(self, warning: str) -> str:
        """Classify warning severity based on content."""
        warning_lower = warning.lower()

        if any(term in warning_lower for term in ["avoid", "contraindicated", "dangerous", "life-threatening"]):
            return "critical"

        elif any(term in warning_lower for term in ["high risk", "severe", "serious"]):
            return "high"

        elif any(term in warning_lower for term in ["moderate risk", "caution", "monitor"]):
            return "moderate"

        else:
            return "low"

    def _categorize_warning(self, warning: str) -> str:
        """Categorize warning by type."""
        warning_lower = warning.lower()

        if "age" in warning_lower or "pediatric" in warning_lower or "geriatric" in warning_lower:
            return "age_related"

        elif "beers" in warning_lower:
            return "beers_criteria"

        elif any(term in warning_lower for term in ["interaction", "combination"]):
            return "drug_interaction"

        elif any(term in warning_lower for term in ["dose", "dosage", "mg", "ml"]):
            return "dosage_related"

        elif any(term in warning_lower for term in ["condition", "disease", "failure"]):
            return "condition_related"

        else:
            return "general"

    def compare_risk_scores(self, assessments: List[Dict]) -> Dict:
        """
        Compare risk scores across multiple drug assessments.

        Args:
            assessments: List of drug assessment dictionaries

        Returns:
            Comparison summary
        """
        if not assessments:
            return {"error": "No assessments provided"}

        scores = [self.calculate_risk_score(assessment) for assessment in assessments]

        comparison = {
            "total_assessments": len(assessments),
            "average_score": round(sum(scores) / len(scores), 2),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "score_distribution": {
                "low": len([s for s in scores if s < 4.0]),
                "moderate": len([s for s in scores if 4.0 <= s < 6.0]),
                "high": len([s for s in scores if 6.0 <= s < 8.0]),
                "critical": len([s for s in scores if s >= 8.0])
            }
        }

        # Find highest risk drug
        max_score_idx = scores.index(max(scores))
        comparison["highest_risk_drug"] = assessments[max_score_idx].get("drug_name", "Unknown")

        return comparison
