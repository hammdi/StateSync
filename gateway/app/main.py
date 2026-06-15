"""
StateSync API Gateway v2
~~~~~~~~~~~~~~~~~~~~~~~~
Central bus: citizen data, service requests, document generation,
OTP authentication, access control matrix, employee portal, audit trail.
"""

import hashlib
import json
import random
from datetime import datetime, timedelta

import httpx
import redis
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .access_control import ACCESS_MATRIX, MINISTRY_LABELS, can_access
from .auth import create_access_token, verify_token
from .config import settings
from .database import get_db
from .document_generator import generate_document, generate_reference
from .models import (
    AuditLog, ApiKey, Appointment, AppointmentSlot, Citizen, DataShare,
    Delegation, Document, Employee, ErrorReport, OtpCode, ServiceRequest,
)
from .pdf_generator import generate_pdf
from .services_catalog import CATALOG
from .bundles_catalog import BUNDLES, LIFE_EVENTS
from .smart_assistant import compute_completeness, generate_reminders, generate_suggestions

app = FastAPI(
    title="StateSync Gateway",
    description="National data synchronization — secure, audited, zero direct DB access",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis
try:
    redis_client: redis.Redis | None = redis.Redis.from_url(
        settings.REDIS_URL, decode_responses=True
    )
    redis_client.ping()
except Exception:
    redis_client = None

MINISTRIES = {
    "civil": settings.MINISTRY_CIVIL_URL,
    "education": settings.MINISTRY_EDUCATION_URL,
    "defense": settings.MINISTRY_DEFENSE_URL,
    "health": settings.MINISTRY_HEALTH_URL,
    "justice": settings.MINISTRY_JUSTICE_URL,
    "finance": settings.MINISTRY_FINANCE_URL,
    "social": settings.MINISTRY_SOCIAL_URL,
    "transport": settings.MINISTRY_TRANSPORT_URL,
    "property": settings.MINISTRY_PROPERTY_URL,
}

CACHE_TTL = 300


# ── Pydantic schemas ──────────────────────────────

class OtpRequest(BaseModel):
    cin: str

class OtpVerify(BaseModel):
    cin: str
    code: str

class ErrorReportSubmit(BaseModel):
    ministry: str
    field_name: str
    current_value: str = ""
    correct_value: str
    evidence: str = ""

class RequestSubmission(BaseModel):
    cin: str
    ministry: str
    service_id: str
    details: dict = {}

class EmployeeLoginPayload(BaseModel):
    username: str
    password: str

class RequestAction(BaseModel):
    action: str
    note: str = ""

class MinistryUpdate(BaseModel):
    cin: str
    model_config = {"extra": "allow"}


# ── Helpers ───────────────────────────────────────

def _cache_get(key: str) -> str | None:
    if not redis_client:
        return None
    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None

def _cache_set(key: str, value: str, ttl: int = CACHE_TTL) -> None:
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, value)
    except redis.RedisError:
        pass

def _cache_delete(key: str) -> None:
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except redis.RedisError:
        pass

def _log_access(db: Session, cin: str, accessed_by: str, purpose: str,
                ministry: str | None = None, action: str = "read") -> None:
    db.add(AuditLog(
        cin_accessed=cin, accessed_by=accessed_by, purpose=purpose,
        ministry=ministry, action=action,
    ))
    db.commit()

async def _fetch_ministry_data(ministry: str, cin: str) -> dict | None:
    url = MINISTRIES.get(ministry)
    if not url:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{url}/data/{cin}")
            if resp.status_code == 200:
                return resp.json()
    except httpx.RequestError:
        pass
    return None

def _serialize_request(r: ServiceRequest) -> dict:
    return {
        "id": str(r.id), "cin": r.cin, "ministry": r.ministry,
        "ministry_label": MINISTRY_LABELS.get(r.ministry, r.ministry),
        "service_type": r.service_type, "service_name": r.service_name,
        "status": r.status, "details": r.details,
        "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
        "processed_at": r.processed_at.isoformat() if r.processed_at else None,
        "processed_by": r.processed_by, "response_note": r.response_note,
        "document_id": str(r.document_id) if r.document_id else None,
    }

def _serialize_document(d: Document, include_content: bool = False) -> dict:
    out = {
        "id": str(d.id), "cin": d.cin, "document_type": d.document_type,
        "ministry": d.ministry, "title": d.title,
        "reference_number": d.reference_number,
        "generated_at": d.generated_at.isoformat() if d.generated_at else None,
        "valid_until": d.valid_until.isoformat() if d.valid_until else None,
    }
    if include_content:
        out["content"] = d.content
    return out


# ══════════════════════════════════════════════════
#  PUBLIC ENDPOINTS
# ══════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway", "version": "2.0.0"}


@app.get("/ministries")
async def list_ministries():
    """List all ministries and their status."""
    statuses = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in MINISTRIES.items():
            try:
                resp = await client.get(f"{url}/health")
                statuses[name] = {
                    "label": MINISTRY_LABELS.get(name, name),
                    "url": url,
                    "status": "online" if resp.status_code == 200 else "error",
                }
            except httpx.RequestError:
                statuses[name] = {
                    "label": MINISTRY_LABELS.get(name, name),
                    "url": url,
                    "status": "offline",
                }
    return {"ministries": statuses, "access_matrix": ACCESS_MATRIX}


# ══════════════════════════════════════════════════
#  OTP AUTHENTICATION
# ══════════════════════════════════════════════════

@app.post("/auth/otp/request")
async def request_otp(body: OtpRequest, db: Session = Depends(get_db)):
    """Send OTP to citizen's registered phone. (Demo: logged to console.)"""
    citizen = db.query(Citizen).filter(Citizen.cin == body.cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    code = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=5)

    db.add(OtpCode(cin=body.cin, code=code, expires_at=expires))
    db.commit()

    # Production: send SMS. Demo: print to gateway console.
    print(f"\n{'='*50}")
    print(f"  OTP for {citizen.full_name} (CIN: {body.cin})")
    print(f"  Phone: {citizen.phone}")
    print(f"  Code:  {code}")
    print(f"  Expires: {expires.isoformat()}")
    print(f"{'='*50}\n")

    phone_hint = f"***{citizen.phone[-4:]}" if citizen.phone and len(citizen.phone) >= 4 else None
    return {"message": "OTP sent to registered phone", "phone_hint": phone_hint}


@app.post("/auth/otp/verify")
async def verify_otp(body: OtpVerify, db: Session = Depends(get_db)):
    """Verify OTP and return JWT token."""
    otp = (
        db.query(OtpCode)
        .filter(
            OtpCode.cin == body.cin,
            OtpCode.code == body.code,
            OtpCode.used.is_(False),
            OtpCode.expires_at > datetime.utcnow(),
        )
        .order_by(OtpCode.created_at.desc())
        .first()
    )
    if not otp:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    otp.used = True
    db.commit()

    citizen = db.query(Citizen).filter(Citizen.cin == body.cin).first()
    token = create_access_token({
        "sub": body.cin, "role": "citizen", "name": citizen.full_name,
    })
    return {
        "access_token": token, "token_type": "bearer",
        "citizen": {"cin": body.cin, "full_name": citizen.full_name, "phone": citizen.phone},
    }


# ══════════════════════════════════════════════════
#  CITIZEN ENDPOINTS
# ══════════════════════════════════════════════════

@app.get("/citizen/{cin}")
async def get_citizen_data(cin: str, db: Session = Depends(get_db)):
    """Aggregate ALL citizen data from every ministry. Audited."""
    cached = _cache_get(f"citizen:{cin}")
    if cached:
        _log_access(db, cin, "citizen-portal", "Data consultation (cached)")
        return json.loads(cached)

    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    result = {
        "cin": citizen.cin, "full_name": citizen.full_name,
        "birth_date": citizen.birth_date.isoformat(),
        "birth_place": citizen.birth_place,
        "nationality": citizen.nationality,
        "phone": citizen.phone,
        "ministries": {},
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in MINISTRIES.items():
            try:
                resp = await client.get(f"{url}/data/{cin}")
                if resp.status_code == 200:
                    result["ministries"][name] = resp.json()
                elif resp.status_code == 404:
                    result["ministries"][name] = None
                else:
                    result["ministries"][name] = {"error": "Service error"}
            except httpx.RequestError:
                result["ministries"][name] = {"error": "Service unavailable"}

    _cache_set(f"citizen:{cin}", json.dumps(result, default=str))
    _log_access(db, cin, "citizen-portal", "Data consultation")
    return result


@app.get("/citizen/{cin}/audit")
async def get_audit_trail(cin: str, db: Session = Depends(get_db)):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.cin_accessed == cin)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    return [
        {
            "id": str(l.id), "cin_accessed": l.cin_accessed,
            "accessed_by": l.accessed_by, "ministry": l.ministry,
            "action": l.action, "purpose": l.purpose,
            "timestamp": l.timestamp.isoformat(),
        }
        for l in logs
    ]


@app.get("/citizen/{cin}/completeness")
async def get_completeness(cin: str, db: Session = Depends(get_db)):
    """Calculate data completeness score across all ministries."""
    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    citizen_dict = {
        "cin": citizen.cin, "full_name": citizen.full_name,
        "birth_date": citizen.birth_date.isoformat() if citizen.birth_date else None,
        "birth_place": citizen.birth_place, "nationality": citizen.nationality, "phone": citizen.phone,
    }
    ministries_data = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in MINISTRIES.items():
            try:
                resp = await client.get(f"{url}/data/{cin}")
                ministries_data[name] = resp.json() if resp.status_code == 200 else None
            except httpx.RequestError:
                ministries_data[name] = None
    return compute_completeness(citizen_dict, ministries_data)


@app.get("/citizen/{cin}/reminders")
async def get_reminders(cin: str, db: Session = Depends(get_db)):
    """Get proactive reminders and alerts based on citizen data."""
    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    citizen_dict = {
        "cin": citizen.cin, "full_name": citizen.full_name,
        "birth_date": citizen.birth_date.isoformat() if citizen.birth_date else None,
        "birth_place": citizen.birth_place, "nationality": citizen.nationality, "phone": citizen.phone,
    }
    ministries_data = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in MINISTRIES.items():
            try:
                resp = await client.get(f"{url}/data/{cin}")
                ministries_data[name] = resp.json() if resp.status_code == 200 else None
            except httpx.RequestError:
                ministries_data[name] = None
    return {"reminders": generate_reminders(citizen_dict, ministries_data)}


@app.get("/citizen/{cin}/assistant")
async def get_assistant_suggestions(cin: str, db: Session = Depends(get_db)):
    """Smart assistant: personalized suggestions based on citizen profile."""
    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    citizen_dict = {
        "cin": citizen.cin, "full_name": citizen.full_name,
        "birth_date": citizen.birth_date.isoformat() if citizen.birth_date else None,
        "birth_place": citizen.birth_place, "nationality": citizen.nationality, "phone": citizen.phone,
    }
    ministries_data = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in MINISTRIES.items():
            try:
                resp = await client.get(f"{url}/data/{cin}")
                ministries_data[name] = resp.json() if resp.status_code == 200 else None
            except httpx.RequestError:
                ministries_data[name] = None
    suggestions = generate_suggestions(citizen_dict, ministries_data)
    reminders = generate_reminders(citizen_dict, ministries_data)
    completeness = compute_completeness(citizen_dict, ministries_data)
    return {"citizen": citizen_dict["full_name"], "completeness": completeness["score"],
            "reminders": reminders, "suggestions": suggestions}


@app.get("/citizen/{cin}/{ministry}")
async def get_citizen_ministry_data(cin: str, ministry: str, db: Session = Depends(get_db)):
    """Get a specific ministry's data for a citizen."""
    if ministry not in MINISTRIES:
        raise HTTPException(status_code=404, detail="Ministry not found")
    data = await _fetch_ministry_data(ministry, cin)
    if data is None:
        raise HTTPException(status_code=404, detail="No data found")
    _log_access(db, cin, "citizen-portal", f"Viewed {ministry} data", ministry=ministry)
    return data


# ── Error reports ─────────────────────────────────

@app.post("/citizen/{cin}/report-error")
async def submit_error_report(cin: str, report: ErrorReportSubmit, db: Session = Depends(get_db)):
    """Citizen reports incorrect data."""
    er = ErrorReport(
        cin=cin, ministry=report.ministry, field_name=report.field_name,
        current_value=report.current_value, correct_value=report.correct_value,
        evidence=report.evidence,
    )
    db.add(er)
    db.commit()
    db.refresh(er)
    _log_access(db, cin, "citizen-portal",
                f"Error report: {report.ministry}/{report.field_name}", action="report")
    return {"id": str(er.id), "status": "pending", "message": "Error report submitted"}


@app.get("/citizen/{cin}/error-reports")
async def list_error_reports(cin: str, db: Session = Depends(get_db)):
    rows = db.query(ErrorReport).filter(ErrorReport.cin == cin).order_by(ErrorReport.created_at.desc()).all()
    return [
        {
            "id": str(r.id), "ministry": r.ministry, "field_name": r.field_name,
            "current_value": r.current_value, "correct_value": r.correct_value,
            "status": r.status, "review_note": r.review_note,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
        }
        for r in rows
    ]


# ══════════════════════════════════════════════════
#  MINISTRY-TO-MINISTRY (with access control)
# ══════════════════════════════════════════════════

@app.get("/ministry/{requester}/citizens/{cin}")
async def ministry_read_citizen(
    requester: str, cin: str, db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """A ministry reads citizen data. Access control matrix enforced."""
    emp_ministry = token.get("ministry", "")
    if emp_ministry != "all" and emp_ministry != requester:
        raise HTTPException(status_code=403, detail="Token does not match requester ministry")

    # Gather data from all ALLOWED ministries
    result = {}
    for target_ministry in MINISTRIES:
        if can_access(requester, target_ministry):
            data = await _fetch_ministry_data(target_ministry, cin)
            if data:
                result[target_ministry] = data

    _log_access(db, cin, f"ministry-{requester}",
                f"Cross-ministry read by {requester}", ministry=requester)
    return {"cin": cin, "requester": requester, "data": result}


@app.post("/ministry/{name}/citizens/{cin}")
async def ministry_update_citizen(
    name: str, cin: str, data: dict, db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Ministry updates its OWN data only."""
    emp_ministry = token.get("ministry", "")
    if emp_ministry != "all" and emp_ministry != name:
        raise HTTPException(status_code=403, detail="A ministry can only update its own data")

    if name not in MINISTRIES:
        raise HTTPException(status_code=404, detail="Ministry not found")

    url = MINISTRIES[name]
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.put(f"{url}/data/{cin}", json=data)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Update failed")

    _cache_delete(f"citizen:{cin}")
    _log_access(db, cin, f"ministry-{name}", f"Data update by {name}", ministry=name, action="update")
    return resp.json()


@app.get("/ministry/{name}/stats")
async def ministry_stats(name: str, db: Session = Depends(get_db)):
    """Ministry statistics."""
    if name not in MINISTRIES:
        raise HTTPException(status_code=404, detail="Ministry not found")
    total_requests = db.query(ServiceRequest).filter(ServiceRequest.ministry == name).count()
    pending = db.query(ServiceRequest).filter(ServiceRequest.ministry == name, ServiceRequest.status == "pending").count()
    error_reports = db.query(ErrorReport).filter(ErrorReport.ministry == name, ErrorReport.status == "pending").count()
    return {
        "ministry": name, "label": MINISTRY_LABELS.get(name),
        "total_requests": total_requests, "pending_requests": pending,
        "pending_error_reports": error_reports,
    }


# ══════════════════════════════════════════════════
#  SERVICE CATALOG & REQUESTS
# ══════════════════════════════════════════════════

@app.get("/services")
async def list_services():
    return {"catalog": CATALOG, "labels": MINISTRY_LABELS}

@app.get("/services/{ministry}")
async def get_ministry_services(ministry: str):
    if ministry not in CATALOG:
        raise HTTPException(status_code=404, detail="Ministry not found")
    return {"ministry": ministry, "label": MINISTRY_LABELS.get(ministry), "services": CATALOG[ministry]}

@app.post("/requests")
async def submit_request(req: RequestSubmission, db: Session = Depends(get_db)):
    citizen = db.query(Citizen).filter(Citizen.cin == req.cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    service = None
    for s in CATALOG.get(req.ministry, []):
        if s["id"] == req.service_id:
            service = s
            break
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    sr = ServiceRequest(
        cin=req.cin, ministry=req.ministry, service_type=req.service_id,
        service_name=service["name"], details=req.details, status="pending",
    )

    if service.get("auto_approve"):
        sr.status = "approved"
        sr.processed_at = datetime.utcnow()
        sr.processed_by = "system (auto)"
        sr.response_note = "Automatically approved"
        ministry_data = await _fetch_ministry_data(req.ministry, req.cin)
        citizen_dict = {
            "cin": citizen.cin, "full_name": citizen.full_name,
            "birth_date": citizen.birth_date.isoformat(), "nationality": citizen.nationality,
        }
        doc_content = generate_document(req.service_id, citizen_dict, req.ministry, ministry_data, req.details)
        doc = Document(
            cin=req.cin, document_type=req.service_id, ministry=req.ministry,
            title=doc_content["title"], content=doc_content,
            reference_number=doc_content["reference"], valid_until=doc_content.get("valid_until"),
        )
        db.add(doc)
        db.flush()
        sr.document_id = doc.id

    db.add(sr)
    db.commit()
    db.refresh(sr)
    _log_access(db, req.cin, "citizen-portal", f"Service request: {service['name']}", action="request")
    return _serialize_request(sr)

@app.get("/requests/{cin}")
async def list_requests(cin: str, db: Session = Depends(get_db)):
    rows = db.query(ServiceRequest).filter(ServiceRequest.cin == cin).order_by(ServiceRequest.submitted_at.desc()).all()
    return [_serialize_request(r) for r in rows]


# ══════════════════════════════════════════════════
#  DOCUMENTS
# ══════════════════════════════════════════════════

@app.get("/documents/{cin}")
async def list_documents(cin: str, db: Session = Depends(get_db)):
    rows = db.query(Document).filter(Document.cin == cin).order_by(Document.generated_at.desc()).all()
    return [_serialize_document(d) for d in rows]

@app.get("/documents/{cin}/{doc_id}")
async def get_document(cin: str, doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.cin == cin).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    _log_access(db, cin, "citizen-portal", f"Document accessed: {doc.title}")
    return _serialize_document(doc, include_content=True)

@app.get("/documents/{cin}/{doc_id}/pdf")
async def get_document_pdf(cin: str, doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.cin == cin).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    _log_access(db, cin, "citizen-portal", f"PDF downloaded: {doc.title}")
    pdf_bytes = generate_pdf(doc.content)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{doc.reference_number}.pdf"'},
    )


# ══════════════════════════════════════════════════
#  EMPLOYEE PORTAL
# ══════════════════════════════════════════════════

@app.post("/employee/login")
async def employee_login(creds: EmployeeLoginPayload, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.username == creds.username, Employee.active.is_(True)).first()
    if not emp:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if hashlib.sha256(creds.password.encode()).hexdigest() != emp.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({
        "sub": emp.username, "role": emp.role, "ministry": emp.ministry, "name": emp.full_name,
    })
    return {
        "access_token": token, "token_type": "bearer",
        "employee": {
            "username": emp.username, "full_name": emp.full_name,
            "ministry": emp.ministry, "ministry_label": MINISTRY_LABELS.get(emp.ministry, emp.ministry),
            "role": emp.role,
        },
    }

@app.get("/employee/dashboard")
async def employee_dashboard(db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    ministry = token.get("ministry", "")
    q = db.query(ServiceRequest)
    if ministry != "all":
        q = q.filter(ServiceRequest.ministry == ministry)
    total = q.count()
    pending = q.filter(ServiceRequest.status == "pending").count()
    approved = q.filter(ServiceRequest.status == "approved").count()
    rejected = q.filter(ServiceRequest.status == "rejected").count()
    recent = q.filter(ServiceRequest.status == "pending").order_by(ServiceRequest.submitted_at.asc()).limit(20).all()
    # Error reports for this ministry
    eq = db.query(ErrorReport)
    if ministry != "all":
        eq = eq.filter(ErrorReport.ministry == ministry)
    pending_errors = eq.filter(ErrorReport.status == "pending").count()
    return {
        "employee": {"name": token.get("name"), "ministry": ministry},
        "stats": {"total": total, "pending": pending, "approved": approved, "rejected": rejected, "pending_errors": pending_errors},
        "pending_requests": [_serialize_request(r) for r in recent],
    }

@app.get("/employee/requests")
async def employee_list_requests(status: str = "pending", db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    ministry = token.get("ministry", "")
    q = db.query(ServiceRequest)
    if ministry != "all":
        q = q.filter(ServiceRequest.ministry == ministry)
    if status:
        q = q.filter(ServiceRequest.status == status)
    return [_serialize_request(r) for r in q.order_by(ServiceRequest.submitted_at.asc()).all()]

@app.put("/employee/requests/{request_id}")
async def process_request(request_id: str, action: RequestAction, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    sr = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not sr:
        raise HTTPException(status_code=404, detail="Request not found")
    if sr.status != "pending":
        raise HTTPException(status_code=400, detail="Already processed")
    emp_ministry = token.get("ministry", "")
    if emp_ministry != "all" and emp_ministry != sr.ministry:
        raise HTTPException(status_code=403, detail="Not authorized for this ministry")
    sr.status = "approved" if action.action == "approve" else "rejected"
    sr.processed_at = datetime.utcnow()
    sr.processed_by = token.get("name", token.get("sub"))
    sr.response_note = action.note or f"Request {sr.status}"
    if action.action == "approve":
        citizen = db.query(Citizen).filter(Citizen.cin == sr.cin).first()
        if citizen:
            ministry_data = await _fetch_ministry_data(sr.ministry, sr.cin)
            citizen_dict = {
                "cin": citizen.cin, "full_name": citizen.full_name,
                "birth_date": citizen.birth_date.isoformat(), "nationality": citizen.nationality,
            }
            doc_content = generate_document(sr.service_type, citizen_dict, sr.ministry, ministry_data, sr.details or {})
            doc = Document(
                cin=sr.cin, document_type=sr.service_type, ministry=sr.ministry,
                title=doc_content["title"], content=doc_content,
                reference_number=generate_reference(sr.ministry, sr.cin),
                valid_until=doc_content.get("valid_until"), request_id=sr.id,
            )
            db.add(doc)
            db.flush()
            sr.document_id = doc.id
    db.commit()
    _log_access(db, sr.cin, f"employee:{token.get('sub')}", f"Request {sr.status}: {sr.service_name}", action="process")
    return _serialize_request(sr)


# ══════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════

@app.get("/admin/stats")
async def admin_stats(db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    if token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    citizens = db.query(Citizen).count()
    audits = db.query(AuditLog).count()
    requests = db.query(ServiceRequest).count()
    documents = db.query(Document).count()
    errors = db.query(ErrorReport).filter(ErrorReport.status == "pending").count()
    return {
        "citizens": citizens, "audit_entries": audits,
        "total_requests": requests, "total_documents": documents,
        "pending_error_reports": errors, "ministries": len(MINISTRIES),
    }

@app.get("/admin/error-reports")
async def admin_error_reports(db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    if token.get("role") != "admin" and token.get("ministry") == "all":
        pass  # admin can see all
    ministry = token.get("ministry")
    q = db.query(ErrorReport)
    if ministry != "all":
        q = q.filter(ErrorReport.ministry == ministry)
    rows = q.order_by(ErrorReport.created_at.desc()).all()
    return [
        {
            "id": str(r.id), "cin": r.cin, "ministry": r.ministry,
            "field_name": r.field_name, "current_value": r.current_value,
            "correct_value": r.correct_value, "evidence": r.evidence,
            "status": r.status, "reviewed_by": r.reviewed_by,
            "review_note": r.review_note,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

@app.put("/admin/error-reports/{report_id}")
async def resolve_error_report(report_id: str, action: RequestAction, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    er = db.query(ErrorReport).filter(ErrorReport.id == report_id).first()
    if not er:
        raise HTTPException(status_code=404, detail="Report not found")
    er.status = "resolved" if action.action == "approve" else "rejected"
    er.reviewed_by = token.get("name", token.get("sub"))
    er.reviewed_at = datetime.utcnow()
    er.review_note = action.note
    db.commit()
    return {"id": str(er.id), "status": er.status}


# ══════════════════════════════════════════════════
#  PUBLIC DOCUMENT VERIFICATION
# ══════════════════════════════════════════════════

@app.get("/public/verify/{reference}")
async def verify_document(reference: str, db: Session = Depends(get_db)):
    """Public endpoint — anyone can verify a document's authenticity. No login required."""
    doc = db.query(Document).filter(Document.reference_number == reference).first()
    if not doc:
        return {"valid": False, "message": "Document not found in the system"}

    citizen = db.query(Citizen).filter(Citizen.cin == doc.cin).first()
    is_expired = bool(doc.valid_until and doc.valid_until < datetime.utcnow().date())

    return {
        "valid": not is_expired,
        "expired": is_expired,
        "document": {
            "title": doc.title,
            "ministry": doc.ministry,
            "ministry_label": MINISTRY_LABELS.get(doc.ministry, doc.ministry),
            "reference": doc.reference_number,
            "citizen_name": citizen.full_name if citizen else "Unknown",
            "cin_masked": f"****{doc.cin[-4:]}" if doc.cin else "",
            "issued": doc.generated_at.isoformat() if doc.generated_at else None,
            "valid_until": doc.valid_until.isoformat() if doc.valid_until else "Permanent",
        },
    }


# ══════════════════════════════════════════════════
#  DOCUMENT BUNDLES
# ══════════════════════════════════════════════════

@app.get("/bundles")
async def list_bundles():
    """List all available document bundles."""
    return {"bundles": {k: {**v, "document_count": len(v["services"])} for k, v in BUNDLES.items()}}


@app.post("/bundles/{bundle_id}")
async def request_bundle(bundle_id: str, cin: str, db: Session = Depends(get_db)):
    """Request all documents in a bundle at once."""
    bundle = BUNDLES.get(bundle_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")

    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    results = []
    for svc_def in bundle["services"]:
        # Find service in catalog
        service = None
        for s in CATALOG.get(svc_def["ministry"], []):
            if s["id"] == svc_def["service_id"]:
                service = s
                break
        if not service:
            continue

        details = svc_def.get("default_details", {})
        sr = ServiceRequest(
            cin=cin, ministry=svc_def["ministry"], service_type=svc_def["service_id"],
            service_name=service["name"], details=details, status="pending",
        )

        # Auto-approve if applicable
        if service.get("auto_approve"):
            sr.status = "approved"
            sr.processed_at = datetime.utcnow()
            sr.processed_by = "system (auto)"
            sr.response_note = f"Auto-approved (bundle: {bundle['name']})"
            ministry_data = await _fetch_ministry_data(svc_def["ministry"], cin)
            citizen_dict = {
                "cin": citizen.cin, "full_name": citizen.full_name,
                "birth_date": citizen.birth_date.isoformat(), "nationality": citizen.nationality,
            }
            doc_content = generate_document(svc_def["service_id"], citizen_dict, svc_def["ministry"], ministry_data, details)
            doc = Document(
                cin=cin, document_type=svc_def["service_id"], ministry=svc_def["ministry"],
                title=doc_content["title"], content=doc_content,
                reference_number=doc_content["reference"], valid_until=doc_content.get("valid_until"),
            )
            db.add(doc)
            db.flush()
            sr.document_id = doc.id

        db.add(sr)
        results.append(_serialize_request(sr))

    db.commit()
    _log_access(db, cin, "citizen-portal", f"Bundle requested: {bundle['name']}", action="bundle")

    approved = sum(1 for r in results if r["status"] == "approved")
    pending = sum(1 for r in results if r["status"] == "pending")
    return {
        "bundle": bundle_id,
        "bundle_name": bundle["name"],
        "total": len(results),
        "approved_instantly": approved,
        "pending_review": pending,
        "requests": results,
    }


# ══════════════════════════════════════════════════
#  LIFE EVENTS
# ══════════════════════════════════════════════════

@app.get("/life-events")
async def list_life_events():
    """List all available life event workflows."""
    return {
        "events": {
            k: {"name": v["name"], "icon": v["icon"], "description": v["description"], "steps": len(v["steps"])}
            for k, v in LIFE_EVENTS.items()
        }
    }


@app.get("/life-events/{event_id}")
async def get_life_event_details(event_id: str):
    """Get full details of a life event workflow."""
    event = LIFE_EVENTS.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life event not found")
    return event


@app.post("/life-events/{event_id}")
async def start_life_event(event_id: str, cin: str, db: Session = Depends(get_db)):
    """Start a life event — creates all required service requests as a tracked workflow."""
    event = LIFE_EVENTS.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life event not found")

    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    steps_results = []
    for step in event["steps"]:
        service = None
        for s in CATALOG.get(step["ministry"], []):
            if s["id"] == step["service_id"]:
                service = s
                break
        if not service:
            continue

        details = step.get("details", {})
        sr = ServiceRequest(
            cin=cin, ministry=step["ministry"], service_type=step["service_id"],
            service_name=service["name"], details=details, status="pending",
        )

        if service.get("auto_approve"):
            sr.status = "approved"
            sr.processed_at = datetime.utcnow()
            sr.processed_by = "system (auto)"
            sr.response_note = f"Auto-approved (life event: {event['name']})"
            ministry_data = await _fetch_ministry_data(step["ministry"], cin)
            citizen_dict = {
                "cin": citizen.cin, "full_name": citizen.full_name,
                "birth_date": citizen.birth_date.isoformat(), "nationality": citizen.nationality,
            }
            doc_content = generate_document(step["service_id"], citizen_dict, step["ministry"], ministry_data, details)
            doc = Document(
                cin=cin, document_type=step["service_id"], ministry=step["ministry"],
                title=doc_content["title"], content=doc_content,
                reference_number=doc_content["reference"], valid_until=doc_content.get("valid_until"),
            )
            db.add(doc)
            db.flush()
            sr.document_id = doc.id

        db.add(sr)
        steps_results.append({
            "order": step["order"],
            "label": step["label"],
            "phase": step["phase"],
            "request": _serialize_request(sr),
        })

    db.commit()
    _log_access(db, cin, "citizen-portal", f"Life event started: {event['name']}", action="life-event")

    completed = sum(1 for s in steps_results if s["request"]["status"] == "approved")
    total = len(steps_results)

    return {
        "event_id": event_id,
        "event_name": event["name"],
        "total_steps": total,
        "completed": completed,
        "pending": total - completed,
        "progress_percent": round(completed / total * 100) if total else 0,
        "steps": steps_results,
    }


# ══════════════════════════════════════════════════
#  WEBSOCKET REAL-TIME NOTIFICATIONS
# ══════════════════════════════════════════════════

_ws_clients: dict[str, list[WebSocket]] = {}


@app.websocket("/ws/citizen/{cin}")
async def websocket_endpoint(websocket: WebSocket, cin: str):
    """Real-time notifications for a citizen."""
    await websocket.accept()
    _ws_clients.setdefault(cin, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _ws_clients.get(cin, []).remove(websocket)


async def _notify(cin: str, event_type: str, message: str, data: dict | None = None):
    """Push a notification to all connected WebSocket clients for a CIN."""
    payload = {"type": event_type, "message": message, "data": data or {},
               "timestamp": datetime.utcnow().isoformat()}
    for ws in _ws_clients.get(cin, []):
        try:
            await ws.send_json(payload)
        except Exception:
            pass


# ══════════════════════════════════════════════════
#  CONSENT MANAGEMENT / DATA SHARING
# ══════════════════════════════════════════════════


class ShareCreatePayload(BaseModel):
    cin: str
    recipient_name: str
    purpose: str = ""
    ministries: list[str]
    expires_hours: int = 24
    one_time: bool = False


@app.post("/shares")
async def create_share(body: ShareCreatePayload, db: Session = Depends(get_db)):
    """Citizen creates a data share link with scoped permissions."""
    citizen = db.query(Citizen).filter(Citizen.cin == body.cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Validate ministries
    for m in body.ministries:
        if m not in MINISTRIES:
            raise HTTPException(status_code=400, detail=f"Unknown ministry: {m}")

    import secrets
    token = secrets.token_urlsafe(32)
    code = str(random.randint(100000, 999999))

    share = DataShare(
        cin=body.cin, token=token, access_code=code,
        recipient_name=body.recipient_name, purpose=body.purpose,
        ministries=body.ministries,
        expires_at=datetime.utcnow() + timedelta(hours=body.expires_hours),
        one_time=body.one_time,
    )
    db.add(share)
    db.commit()
    db.refresh(share)

    _log_access(db, body.cin, "citizen-portal",
                f"Data share created for {body.recipient_name}: {body.ministries}", action="share")

    return {
        "token": token, "access_code": code,
        "share_url": f"/public/shared/{token}",
        "recipient": body.recipient_name,
        "ministries": body.ministries,
        "expires_at": share.expires_at.isoformat(),
        "one_time": body.one_time,
    }


@app.get("/shares/{cin}")
async def list_shares(cin: str, db: Session = Depends(get_db)):
    """List all active data shares for a citizen."""
    rows = (
        db.query(DataShare)
        .filter(DataShare.cin == cin)
        .order_by(DataShare.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(s.id), "token": s.token, "recipient_name": s.recipient_name,
            "purpose": s.purpose, "ministries": s.ministries,
            "expires_at": s.expires_at.isoformat(), "one_time": s.one_time,
            "revoked": s.revoked, "used": s.used, "access_count": s.access_count,
            "active": not s.revoked and s.expires_at.replace(tzinfo=None) > datetime.utcnow() and not (s.one_time and s.used),
            "created_at": s.created_at.isoformat(),
        }
        for s in rows
    ]


@app.delete("/shares/{cin}/{token}")
async def revoke_share(cin: str, token: str, db: Session = Depends(get_db)):
    """Citizen revokes a share link."""
    share = db.query(DataShare).filter(DataShare.cin == cin, DataShare.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    share.revoked = True
    db.commit()
    _log_access(db, cin, "citizen-portal", f"Share revoked: {share.recipient_name}", action="revoke")
    return {"status": "revoked"}


@app.post("/public/shared/{token}")
async def access_shared_data(token: str, access_code: str, db: Session = Depends(get_db)):
    """Third party accesses shared data using token + access code."""
    share = db.query(DataShare).filter(DataShare.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    if share.revoked:
        raise HTTPException(status_code=403, detail="This share has been revoked")
    if share.expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(status_code=403, detail="This share has expired")
    if share.one_time and share.used:
        raise HTTPException(status_code=403, detail="This one-time share has already been used")
    if share.access_code != access_code:
        raise HTTPException(status_code=401, detail="Invalid access code")

    citizen = db.query(Citizen).filter(Citizen.cin == share.cin).first()
    result = {
        "citizen": {"full_name": citizen.full_name, "cin_masked": f"****{share.cin[-4:]}"},
        "shared_by": citizen.full_name,
        "purpose": share.purpose,
        "ministries": {},
    }

    # Fetch ONLY the permitted ministries
    async with httpx.AsyncClient(timeout=5.0) as client:
        for ministry in share.ministries:
            url = MINISTRIES.get(ministry)
            if not url:
                continue
            try:
                resp = await client.get(f"{url}/data/{share.cin}")
                if resp.status_code == 200:
                    result["ministries"][ministry] = resp.json()
            except httpx.RequestError:
                result["ministries"][ministry] = {"error": "Service unavailable"}

    # Update usage
    share.access_count += 1
    if share.one_time:
        share.used = True
    db.commit()

    _log_access(db, share.cin, f"shared:{share.recipient_name}",
                f"Shared data accessed by {share.recipient_name}: {share.ministries}", action="shared-access")

    # Notify citizen
    await _notify(share.cin, "data_accessed",
                  f"{share.recipient_name} accessed your shared data",
                  {"recipient": share.recipient_name, "ministries": share.ministries})

    return result


# ══════════════════════════════════════════════════
#  EMERGENCY ACCESS PROTOCOL
# ══════════════════════════════════════════════════


class EmergencyAccessPayload(BaseModel):
    doctor_name: str
    hospital_id: str
    reason: str


@app.post("/emergency/{cin}")
async def emergency_access(cin: str, body: EmergencyAccessPayload, db: Session = Depends(get_db)):
    """Emergency health data access. Returns critical medical info immediately.
    Bypasses normal auth. Logged with EMERGENCY flag. Citizen notified."""

    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Fetch health data
    health_data = await _fetch_ministry_data("health", cin)

    result = {
        "emergency": True,
        "citizen": {"full_name": citizen.full_name, "cin": cin,
                    "birth_date": citizen.birth_date.isoformat() if citizen.birth_date else None},
        "critical_medical_info": {
            "blood_type": health_data.get("blood_type") if health_data else "UNKNOWN",
            "allergies": health_data.get("allergies", []) if health_data else [],
            "chronic_diseases": health_data.get("chronic_diseases", []) if health_data else [],
            "disabilities": health_data.get("disabilities", []) if health_data else [],
            "organ_donor": health_data.get("organ_donor", False) if health_data else False,
            "vaccinations": health_data.get("vaccinations", []) if health_data else [],
        },
        "accessed_by": {"doctor": body.doctor_name, "hospital": body.hospital_id},
        "reason": body.reason,
        "timestamp": datetime.utcnow().isoformat(),
        "notice": "This access has been logged as EMERGENCY. The citizen will be notified.",
    }

    # Log with EMERGENCY flag
    _log_access(db, cin, f"EMERGENCY:{body.hospital_id}:{body.doctor_name}",
                f"EMERGENCY ACCESS - Reason: {body.reason} - Doctor: {body.doctor_name} - Hospital: {body.hospital_id}",
                ministry="health", action="emergency")

    # Notify citizen via WebSocket
    await _notify(cin, "emergency_access",
                  f"EMERGENCY: Dr. {body.doctor_name} at {body.hospital_id} accessed your health data",
                  {"doctor": body.doctor_name, "hospital": body.hospital_id, "reason": body.reason})

    print(f"\n{'!'*60}")
    print(f"  EMERGENCY ACCESS")
    print(f"  Citizen: {citizen.full_name} (CIN: {cin})")
    print(f"  Doctor: {body.doctor_name}")
    print(f"  Hospital: {body.hospital_id}")
    print(f"  Reason: {body.reason}")
    print(f"  Blood Type: {result['critical_medical_info']['blood_type']}")
    print(f"  Allergies: {result['critical_medical_info']['allergies']}")
    print(f"{'!'*60}\n")

    return result


# ══════════════════════════════════════════════════
#  DELEGATION SYSTEM
# ══════════════════════════════════════════════════


class DelegationPayload(BaseModel):
    citizen_cin: str
    delegate_cin: str
    delegate_name: str
    relationship: str  # parent, lawyer, spouse, employer
    scope: list[str]  # ministry names or ["all"]
    expires_days: int = 30


@app.post("/delegations")
async def create_delegation(body: DelegationPayload, db: Session = Depends(get_db)):
    """Citizen authorizes someone to act on their behalf."""
    citizen = db.query(Citizen).filter(Citizen.cin == body.citizen_cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    d = Delegation(
        citizen_cin=body.citizen_cin, delegate_cin=body.delegate_cin,
        delegate_name=body.delegate_name, relationship=body.relationship,
        scope=body.scope,
        expires_at=datetime.utcnow() + timedelta(days=body.expires_days),
    )
    db.add(d)
    db.commit()
    db.refresh(d)

    _log_access(db, body.citizen_cin, "citizen-portal",
                f"Delegation created: {body.delegate_name} ({body.relationship}) scope={body.scope}", action="delegate")
    return {
        "id": str(d.id), "citizen_cin": d.citizen_cin, "delegate_cin": d.delegate_cin,
        "delegate_name": d.delegate_name, "relationship": d.relationship,
        "scope": d.scope, "expires_at": d.expires_at.isoformat(), "active": True,
    }


@app.get("/delegations/{cin}")
async def list_delegations(cin: str, db: Session = Depends(get_db)):
    """List delegations where citizen is either the delegator or delegate."""
    given = db.query(Delegation).filter(Delegation.citizen_cin == cin).all()
    received = db.query(Delegation).filter(Delegation.delegate_cin == cin).all()

    def serialize(d: Delegation):
        return {
            "id": str(d.id), "citizen_cin": d.citizen_cin, "delegate_cin": d.delegate_cin,
            "delegate_name": d.delegate_name, "relationship": d.relationship,
            "scope": d.scope, "expires_at": d.expires_at.isoformat(),
            "active": d.active and d.expires_at.replace(tzinfo=None) > datetime.utcnow(),
        }

    return {
        "given": [serialize(d) for d in given],
        "received": [serialize(d) for d in received],
    }


@app.delete("/delegations/{cin}/{delegation_id}")
async def revoke_delegation(cin: str, delegation_id: str, db: Session = Depends(get_db)):
    d = db.query(Delegation).filter(Delegation.id == delegation_id, Delegation.citizen_cin == cin).first()
    if not d:
        raise HTTPException(status_code=404, detail="Delegation not found")
    d.active = False
    db.commit()
    return {"status": "revoked"}


@app.get("/delegations/{cin}/act-as/{target_cin}")
async def delegate_view_citizen(cin: str, target_cin: str, db: Session = Depends(get_db)):
    """Delegate views citizen data within their authorized scope."""
    deleg = (
        db.query(Delegation)
        .filter(Delegation.delegate_cin == cin, Delegation.citizen_cin == target_cin,
                Delegation.active.is_(True))
        .first()
    )
    if not deleg or deleg.expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(status_code=403, detail="No active delegation found")

    result = {"cin": target_cin, "delegate": cin, "relationship": deleg.relationship, "ministries": {}}
    allowed = deleg.scope if "all" not in deleg.scope else list(MINISTRIES.keys())

    async with httpx.AsyncClient(timeout=5.0) as client:
        for ministry in allowed:
            url = MINISTRIES.get(ministry)
            if not url:
                continue
            try:
                resp = await client.get(f"{url}/data/{target_cin}")
                if resp.status_code == 200:
                    result["ministries"][ministry] = resp.json()
            except httpx.RequestError:
                pass

    _log_access(db, target_cin, f"delegate:{cin}",
                f"Delegate access by {deleg.delegate_name} ({deleg.relationship})", action="delegate-access")
    return result


# ══════════════════════════════════════════════════
#  APPOINTMENT BOOKING
# ══════════════════════════════════════════════════


@app.get("/appointments/slots")
async def list_available_slots(ministry: str = "", db: Session = Depends(get_db)):
    """List available appointment slots."""
    from sqlalchemy import func as sqlfunc
    q = db.query(AppointmentSlot).filter(
        AppointmentSlot.date >= datetime.utcnow().date(),
        AppointmentSlot.booked < AppointmentSlot.capacity,
    )
    if ministry:
        q = q.filter(AppointmentSlot.ministry == ministry)
    slots = q.order_by(AppointmentSlot.date, AppointmentSlot.time_start).all()
    return [
        {
            "id": str(s.id), "ministry": s.ministry, "location": s.location,
            "date": s.date.isoformat(), "time_start": s.time_start.isoformat(),
            "time_end": s.time_end.isoformat(),
            "available": s.capacity - s.booked,
        }
        for s in slots
    ]


class BookAppointmentPayload(BaseModel):
    cin: str
    slot_id: str
    purpose: str


@app.post("/appointments")
async def book_appointment(body: BookAppointmentPayload, db: Session = Depends(get_db)):
    """Book an appointment slot."""
    slot = db.query(AppointmentSlot).filter(AppointmentSlot.id == body.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.booked >= slot.capacity:
        raise HTTPException(status_code=400, detail="Slot is fully booked")

    import secrets
    ref = f"APT-{slot.ministry.upper()}-{secrets.token_hex(4).upper()}"

    appt = Appointment(
        cin=body.cin, slot_id=slot.id, ministry=slot.ministry,
        purpose=body.purpose, reference=ref,
    )
    slot.booked += 1
    db.add(appt)
    db.commit()
    db.refresh(appt)

    _log_access(db, body.cin, "citizen-portal",
                f"Appointment booked: {slot.ministry} on {slot.date} at {slot.time_start}", action="appointment")
    await _notify(body.cin, "appointment_booked",
                  f"Appointment confirmed at {slot.location} on {slot.date} {slot.time_start}",
                  {"reference": ref})

    return {
        "id": str(appt.id), "reference": ref, "ministry": slot.ministry,
        "location": slot.location, "date": slot.date.isoformat(),
        "time_start": slot.time_start.isoformat(), "time_end": slot.time_end.isoformat(),
        "purpose": body.purpose, "status": "confirmed",
    }


@app.get("/appointments/{cin}")
async def list_appointments(cin: str, db: Session = Depends(get_db)):
    """List all appointments for a citizen."""
    rows = (
        db.query(Appointment, AppointmentSlot)
        .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
        .filter(Appointment.cin == cin)
        .order_by(AppointmentSlot.date.desc())
        .all()
    )
    return [
        {
            "id": str(a.id), "reference": a.reference, "ministry": a.ministry,
            "location": s.location, "date": s.date.isoformat(),
            "time_start": s.time_start.isoformat(), "time_end": s.time_end.isoformat(),
            "purpose": a.purpose, "status": a.status,
        }
        for a, s in rows
    ]


@app.delete("/appointments/{cin}/{appointment_id}")
async def cancel_appointment(cin: str, appointment_id: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.cin == cin).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    slot = db.query(AppointmentSlot).filter(AppointmentSlot.id == appt.slot_id).first()
    if slot:
        slot.booked = max(0, slot.booked - 1)
    appt.status = "cancelled"
    db.commit()
    return {"status": "cancelled"}


# ══════════════════════════════════════════════════
#  ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════


@app.get("/analytics/overview")
async def analytics_overview(db: Session = Depends(get_db)):
    """System-wide analytics."""
    from sqlalchemy import func as sqlfunc

    citizens = db.query(Citizen).count()
    total_requests = db.query(ServiceRequest).count()
    total_documents = db.query(Document).count()
    total_audits = db.query(AuditLog).count()
    pending_requests = db.query(ServiceRequest).filter(ServiceRequest.status == "pending").count()
    pending_errors = db.query(ErrorReport).filter(ErrorReport.status == "pending").count()
    total_shares = db.query(DataShare).count()
    total_appointments = db.query(Appointment).filter(Appointment.status == "confirmed").count()

    # Per-ministry request counts
    ministry_stats = (
        db.query(ServiceRequest.ministry, ServiceRequest.status, sqlfunc.count())
        .group_by(ServiceRequest.ministry, ServiceRequest.status)
        .all()
    )
    by_ministry: dict = {}
    for ministry, status, count in ministry_stats:
        by_ministry.setdefault(ministry, {})[status] = count

    # Recent activity (last 24h)
    from datetime import timedelta as td
    cutoff = datetime.utcnow() - td(hours=24)
    recent_audits = db.query(AuditLog).filter(AuditLog.timestamp > cutoff).count()
    recent_requests = db.query(ServiceRequest).filter(ServiceRequest.submitted_at > cutoff).count()

    return {
        "totals": {
            "citizens": citizens, "requests": total_requests, "documents": total_documents,
            "audit_entries": total_audits, "shares": total_shares, "appointments": total_appointments,
        },
        "pending": {"requests": pending_requests, "error_reports": pending_errors},
        "last_24h": {"audit_entries": recent_audits, "requests": recent_requests},
        "by_ministry": by_ministry,
    }


@app.get("/analytics/ministry/{name}")
async def analytics_ministry(name: str, db: Session = Depends(get_db)):
    """Per-ministry analytics."""
    from sqlalchemy import func as sqlfunc

    if name not in MINISTRIES:
        raise HTTPException(status_code=404, detail="Ministry not found")

    total = db.query(ServiceRequest).filter(ServiceRequest.ministry == name).count()
    approved = db.query(ServiceRequest).filter(ServiceRequest.ministry == name, ServiceRequest.status == "approved").count()
    rejected = db.query(ServiceRequest).filter(ServiceRequest.ministry == name, ServiceRequest.status == "rejected").count()
    pending = db.query(ServiceRequest).filter(ServiceRequest.ministry == name, ServiceRequest.status == "pending").count()
    documents = db.query(Document).filter(Document.ministry == name).count()
    errors = db.query(ErrorReport).filter(ErrorReport.ministry == name).count()

    # Top services
    top_services = (
        db.query(ServiceRequest.service_name, sqlfunc.count().label("cnt"))
        .filter(ServiceRequest.ministry == name)
        .group_by(ServiceRequest.service_name)
        .order_by(sqlfunc.count().desc())
        .limit(5)
        .all()
    )

    return {
        "ministry": name, "label": MINISTRY_LABELS.get(name),
        "requests": {"total": total, "approved": approved, "rejected": rejected, "pending": pending},
        "documents_generated": documents, "error_reports": errors,
        "approval_rate": round(approved / total * 100) if total else 0,
        "top_services": [{"name": s, "count": c} for s, c in top_services],
    }


# ══════════════════════════════════════════════════
#  THIRD-PARTY API
# ══════════════════════════════════════════════════


@app.get("/api/v1/citizen/{cin}")
async def api_v1_citizen(cin: str, api_key: str = "", db: Session = Depends(get_db)):
    """Third-party API: access citizen data with API key (scoped)."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required. Pass ?api_key=sk_...")

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    ak = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.active.is_(True)).first()
    if not ak:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if ak.requests_today >= ak.rate_limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    ak.requests_today += 1
    db.commit()

    citizen = db.query(Citizen).filter(Citizen.cin == cin).first()
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    result = {
        "cin": citizen.cin, "full_name": citizen.full_name,
        "ministries": {},
    }

    # Only return data for scoped ministries
    async with httpx.AsyncClient(timeout=5.0) as client:
        for ministry in ak.scopes:
            url = MINISTRIES.get(ministry)
            if not url:
                continue
            try:
                resp = await client.get(f"{url}/data/{cin}")
                if resp.status_code == 200:
                    result["ministries"][ministry] = resp.json()
            except httpx.RequestError:
                pass

    _log_access(db, cin, f"api:{ak.organization}",
                f"API access by {ak.organization} (scopes: {ak.scopes})", action="api-access")
    return result


@app.get("/api/v1/verify/{reference}")
async def api_v1_verify(reference: str, api_key: str = "", db: Session = Depends(get_db)):
    """Third-party API: verify a document."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    ak = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.active.is_(True)).first()
    if not ak:
        raise HTTPException(status_code=401, detail="Invalid API key")

    doc = db.query(Document).filter(Document.reference_number == reference).first()
    if not doc:
        return {"valid": False}

    return {
        "valid": True,
        "document": {"title": doc.title, "ministry": doc.ministry, "issued": doc.generated_at.isoformat()},
    }
