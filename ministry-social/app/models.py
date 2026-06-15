from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class SocialRecord(Base):
    __tablename__ = "social_records"

    cin = Column(String(20), primary_key=True)
    social_number = Column(String(50))
    employment_history = Column(JSONB, default=list)
    pension_points = Column(Integer, default=0)
    contributions = Column(JSONB, default=list)
    benefits = Column(JSONB, default=list)
    unemployment_status = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
