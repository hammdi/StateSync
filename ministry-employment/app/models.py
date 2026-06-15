from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class EmploymentRecord(Base):
    __tablename__ = "employment_records"

    cin = Column(String(20), primary_key=True)
    employment_status = Column(String(50), default="Employed")
    current_employer = Column(String(255))
    contracts = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
