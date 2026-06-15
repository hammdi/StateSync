"""Ministry of Transport — manages driver's licenses and vehicle registrations."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import TransportRecord

app = FastAPI(title="Ministry of Transport", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-transport"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(TransportRecord).filter(TransportRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "driving_license": record.driving_license,
        "vehicles": record.vehicles,
        "traffic_violations": record.traffic_violations,
        "technical_inspections": record.technical_inspections,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(TransportRecord).filter(TransportRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "driving_license" in data:
        record.driving_license = data["driving_license"]
    if "vehicles" in data:
        record.vehicles = data["vehicles"]
    if "traffic_violations" in data:
        record.traffic_violations = data["traffic_violations"]
    if "technical_inspections" in data:
        record.technical_inspections = data["technical_inspections"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
