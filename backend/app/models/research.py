from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class Research(Base):
    __tablename__ = "research"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    source = Column(String)
    url = Column(String)
    published_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
