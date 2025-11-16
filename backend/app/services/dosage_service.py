from ..schemas.dosage import DosageRequest, DosageResponse

class DosageService:
    @staticmethod
    def calculate_dosage(request: DosageRequest) -> DosageResponse:
        # Simplified dosage calculation
        # In a real app, this would use comprehensive drug databases
        weight = request.weight
        age = request.age
        medication = request.medication.lower()

        warnings = []
        adjustments = []
        calculation_method = "Standard mg/kg dosing"

        # Basic mg/kg calculation for common medications
        if "paracetamol" in medication or "acetaminophen" in medication:
            base_dose = 15  # mg/kg
            max_dose = 60  # mg/kg/day
            recommended = min(base_dose * weight, max_dose * weight)
            dosage = f"{recommended:.1f} mg every 4-6 hours"
        elif "ibuprofen" in medication:
            base_dose = 10  # mg/kg
            max_dose = 40  # mg/kg/day
            recommended = min(base_dose * weight, max_dose * weight)
            dosage = f"{recommended:.1f} mg every 6-8 hours"
        else:
            dosage = "Consult physician for appropriate dosage"
            calculation_method = "Physician consultation required"

        # Age adjustments
        if age < 2:
            warnings.append("Extreme caution required for infants")
        elif age > 65:
            adjustments.append("Consider reduced dosage for geriatric patients")

        return DosageResponse(
            recommended_dosage=dosage,
            calculation_method=calculation_method,
            warnings=warnings if warnings else None,
            adjustments=adjustments if adjustments else None
        )
