from ..schemas.age_check import AgeCheckRequest, AgeCheckResponse

class AgeService:
    @staticmethod
    def verify_age_safety(request: AgeCheckRequest) -> AgeCheckResponse:
        # Simplified age verification logic
        # In a real app, this would integrate with Beers Criteria, etc.
        age = request.age
        medication = request.medication.lower()

        warnings = []
        recommendations = []
        risk_level = "low"

        if age < 18:
            risk_level = "high"
            warnings.append("Medication may not be approved for pediatric use")
            recommendations.append("Consult pediatrician before use")
        elif age > 65:
            risk_level = "medium"
            warnings.append("Geriatric patients may require dosage adjustment")
            recommendations.append("Monitor for side effects")

        # Add medication-specific checks
        if "aspirin" in medication and age < 18:
            warnings.append("Aspirin use in children may increase Reye's syndrome risk")

        is_safe = risk_level != "high"

        return AgeCheckResponse(
            is_safe=is_safe,
            risk_level=risk_level,
            recommendations=recommendations if recommendations else None,
            warnings=warnings if warnings else None
        )
