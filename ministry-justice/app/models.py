from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class JusticeRecord(Base):
    __tablename__ = "justice_records"

    cin = Column(String(20), primary_key=True)
    criminal_record = Column(String(20))
    cases = Column(JSONB, default=list)
    sentences = Column(JSONB, default=list)
    restrictions = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
