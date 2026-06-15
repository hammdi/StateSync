from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class EducationRecord(Base):
    __tablename__ = "education_records"

    cin = Column(String(20), primary_key=True)
    diplomas = Column(JSONB, default=list)
    equivalences = Column(JSONB, default=list)
    scholarships = Column(JSONB, default=list)
    current_enrollment = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
