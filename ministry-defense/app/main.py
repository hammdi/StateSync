"""Ministry of Defense — manages military service status records."""

from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import DefenseRecord

app = FastAPI(title="Ministry of Defense", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-defense"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(DefenseRecord).filter(DefenseRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "military_status": record.military_status,
        "service_start": record.service_start.isoformat() if record.service_start else None,
        "service_end": record.service_end.isoformat() if record.service_end else None,
        "unit": record.unit,
        "rank": record.rank,
        "exemption_reason": record.exemption_reason,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(DefenseRecord).filter(DefenseRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "military_status" in data:
        record.military_status = data["military_status"]
    if "service_start" in data:
        val = data["service_start"]
        record.service_start = date.fromisoformat(val) if val else None
    if "service_end" in data:
        val = data["service_end"]
        record.service_end = date.fromisoformat(val) if val else None
    if "unit" in data:
        record.unit = data["unit"]
    if "rank" in data:
        record.rank = data["rank"]
    if "exemption_reason" in data:
        record.exemption_reason = data["exemption_reason"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
