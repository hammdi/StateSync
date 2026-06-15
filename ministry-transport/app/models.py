from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class TransportRecord(Base):
    __tablename__ = "transport_records"

    cin = Column(String(20), primary_key=True)
    driving_license = Column(JSONB, default=dict)
    vehicles = Column(JSONB, default=list)
    traffic_violations = Column(JSONB, default=list)
    technical_inspections = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
