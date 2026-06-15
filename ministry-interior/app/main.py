"""Ministry of Interior — manages passports and residence permits."""

from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import InteriorRecord

app = FastAPI(title="Ministry of Interior", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-interior"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(InteriorRecord).filter(InteriorRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "passport_number": record.passport_number,
        "passport_expiry": record.passport_expiry.isoformat() if record.passport_expiry else None,
        "residence_permit": record.residence_permit,
        "permit_expiry": record.permit_expiry.isoformat() if record.permit_expiry else None,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(InteriorRecord).filter(InteriorRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "passport_number" in data:
        record.passport_number = data["passport_number"]
    if "passport_expiry" in data:
        val = data["passport_expiry"]
        record.passport_expiry = date.fromisoformat(val) if val else None
    if "residence_permit" in data:
        record.residence_permit = data["residence_permit"]
    if "permit_expiry" in data:
        val = data["permit_expiry"]
        record.permit_expiry = date.fromisoformat(val) if val else None
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
