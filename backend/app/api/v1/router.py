from fastapi import APIRouter
from .endpoints import auth, users, camera, drugs, side_effects, age_verification, dosage, triage, research, logging

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(camera.router, prefix="/camera", tags=["camera"])
api_router.include_router(drugs.router, prefix="/drugs", tags=["drugs"])
api_router.include_router(side_effects.router, prefix="/side-effects", tags=["side-effects"])
api_router.include_router(age_verification.router, prefix="/age-verification", tags=["age-verification"])
api_router.include_router(dosage.router, prefix="/dosage", tags=["dosage"])
api_router.include_router(triage.router, prefix="/triage", tags=["triage"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(logging.router, prefix="/logging", tags=["logging"])
