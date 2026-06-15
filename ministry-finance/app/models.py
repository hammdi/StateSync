from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class FinanceRecord(Base):
    __tablename__ = "finance_records"

    cin = Column(String(20), primary_key=True)
    tax_id = Column(String(50))
    tax_status = Column(String(50), default="Up to date")
    annual_declarations = Column(JSONB, default=list)
    fines = Column(JSONB, default=list)
    company_ownerships = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
