from datetime import datetime

from sqlalchemy import Column, String, Text, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class CivilRecord(Base):
    __tablename__ = "civil_records"

    cin = Column(String(20), primary_key=True)
    address = Column(Text)
    city = Column(String(100))
    marital_status = Column(String(50))
    children = Column(JSONB, default=list)
    parents = Column(JSONB, default=list)
    death_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
