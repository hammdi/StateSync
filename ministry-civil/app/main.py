"""Ministry of Civil Status — manages addresses, marital status, and family data."""

from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import CivilRecord

app = FastAPI(title="Ministry of Civil Status", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-civil"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(CivilRecord).filter(CivilRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "address": record.address,
        "city": record.city,
        "marital_status": record.marital_status,
        "children": record.children,
        "parents": record.parents,
        "death_date": record.death_date.isoformat() if record.death_date else None,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(CivilRecord).filter(CivilRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "address" in data:
        record.address = data["address"]
    if "city" in data:
        record.city = data["city"]
    if "marital_status" in data:
        record.marital_status = data["marital_status"]
    if "children" in data:
        record.children = data["children"]
    if "parents" in data:
        record.parents = data["parents"]
    if "death_date" in data:
        val = data["death_date"]
        record.death_date = date.fromisoformat(val) if val else None
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
