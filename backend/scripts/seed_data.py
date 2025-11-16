#!/usr/bin/env python3
"""
Database seeding script.
"""
from app.core.database import get_db
from app.services.drug_service import DrugService
from app.services.side_effect_service import SideEffectService
from app.schemas.medication import MedicationCreate
from app.schemas.side_effect import SideEffectCreate

def seed_database():
    """Seed database with initial data."""
    db = next(get_db())

    # Sample medications
    medications = [
        MedicationCreate(
            name="Paracetamol",
            generic_name="Acetaminophen",
            description="Pain reliever and fever reducer"
        ),
        MedicationCreate(
            name="Ibuprofen",
            generic_name="Ibuprofen",
            description="NSAID for pain and inflammation"
        ),
        MedicationCreate(
            name="Aspirin",
            generic_name="Acetylsalicylic acid",
            description="Pain reliever and anti-platelet agent"
        ),
    ]

    for med in medications:
        DrugService.create_drug(db, med)

    # Sample side effects
    side_effects = [
        SideEffectCreate(
            medication_id=1,  # Paracetamol
            name="Nausea",
            severity="Mild",
            description="Feeling of sickness"
        ),
        SideEffectCreate(
            medication_id=2,  # Ibuprofen
            name="Stomach upset",
            severity="Mild",
            description="Gastric irritation"
        ),
    ]

    for se in side_effects:
        SideEffectService.create_side_effect(db, se)

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
