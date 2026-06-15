import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .database import Base


class Citizen(Base):
    __tablename__ = "citizens"
    cin = Column(String(20), primary_key=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_place = Column(String(255))
    nationality = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AuditLog(Base):
    """Immutable audit trail. Database rules prevent UPDATE and DELETE."""
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin_accessed = Column(String(20), nullable=False)
    accessed_by = Column(String(100), nullable=False)
    ministry = Column(String(50))
    action = Column(String(50), default="read")
    purpose = Column(Text, nullable=False)
    ip_address = Column(String(45))
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)


class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin = Column(String(20), nullable=False)
    ministry = Column(String(50), nullable=False)
    service_type = Column(String(100), nullable=False)
    service_name = Column(String(255), nullable=False)
    status = Column(String(30), default="pending")
    details = Column(JSONB, default=dict)
    submitted_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True))
    processed_by = Column(String(100))
    response_note = Column(Text)
    document_id = Column(UUID(as_uuid=True))


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin = Column(String(20), nullable=False)
    document_type = Column(String(100), nullable=False)
    ministry = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSONB, nullable=False)
    reference_number = Column(String(50), unique=True, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    valid_until = Column(Date, nullable=True)
    request_id = Column(UUID(as_uuid=True))


class DataShare(Base):
    __tablename__ = "data_shares"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin = Column(String(20), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    access_code = Column(String(10), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    purpose = Column(String(255))
    ministries = Column(JSONB, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    one_time = Column(Boolean, default=False)
    used = Column(Boolean, default=False)
    revoked = Column(Boolean, default=False)
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ErrorReport(Base):
    __tablename__ = "error_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin = Column(String(20), nullable=False)
    ministry = Column(String(50), nullable=False)
    field_name = Column(String(100), nullable=False)
    current_value = Column(Text)
    correct_value = Column(Text, nullable=False)
    evidence = Column(Text)
    status = Column(String(30), default="pending")
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime(timezone=True))
    review_note = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class OtpCode(Base):
    __tablename__ = "otp_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cin = Column(String(20), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Employee(Base):
    __tablename__ = "employees"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    ministry = Column(String(50), nullable=False)
    role = Column(String(50), default="agent")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
