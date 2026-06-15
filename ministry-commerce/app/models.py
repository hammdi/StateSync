from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class CommerceRecord(Base):
    __tablename__ = "commerce_records"

    cin = Column(String(20), primary_key=True)
    businesses = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
