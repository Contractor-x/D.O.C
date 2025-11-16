from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class SideEffect(Base):
    __tablename__ = "side_effects"

    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String)  # mild, moderate, severe
    frequency = Column(String)  # common, uncommon, rare
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    medication = relationship("Medication")
