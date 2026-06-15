from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"

    cin = Column(String(20), primary_key=True)
    blood_type = Column(String(5))
    allergies = Column(JSONB, default=list)
    chronic_diseases = Column(JSONB, default=list)
    vaccinations = Column(JSONB, default=list)
    disabilities = Column(JSONB, default=list)
    organ_donor = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
