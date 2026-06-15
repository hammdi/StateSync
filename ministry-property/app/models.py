from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class PropertyRecord(Base):
    __tablename__ = "property_records"

    cin = Column(String(20), primary_key=True)
    properties = Column(JSONB, default=list)
    mortgages = Column(JSONB, default=list)
    land_registry = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
