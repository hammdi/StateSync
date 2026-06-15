from datetime import datetime

from sqlalchemy import Column, String, Date, DateTime

from .database import Base


class InteriorRecord(Base):
    __tablename__ = "interior_records"

    cin = Column(String(20), primary_key=True)
    passport_number = Column(String(50))
    passport_expiry = Column(Date, nullable=True)
    residence_permit = Column(String(100), nullable=True)
    permit_expiry = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
