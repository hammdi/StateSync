from datetime import datetime

from sqlalchemy import Column, String, Date, DateTime

from .database import Base


class DefenseRecord(Base):
    __tablename__ = "defense_records"

    cin = Column(String(20), primary_key=True)
    military_status = Column(String(50))
    service_start = Column(Date, nullable=True)
    service_end = Column(Date, nullable=True)
    unit = Column(String(255), nullable=True)
    rank = Column(String(100), nullable=True)
    exemption_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
