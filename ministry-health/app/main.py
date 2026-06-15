"""Ministry of Health — manages medical records and vaccination history."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import HealthRecord

app = FastAPI(title="Ministry of Health", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-health"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(HealthRecord).filter(HealthRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "blood_type": record.blood_type,
        "allergies": record.allergies,
        "chronic_diseases": record.chronic_diseases,
        "vaccinations": record.vaccinations,
        "disabilities": record.disabilities,
        "organ_donor": record.organ_donor,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(HealthRecord).filter(HealthRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "blood_type" in data:
        record.blood_type = data["blood_type"]
    if "allergies" in data:
        record.allergies = data["allergies"]
    if "chronic_diseases" in data:
        record.chronic_diseases = data["chronic_diseases"]
    if "vaccinations" in data:
        record.vaccinations = data["vaccinations"]
    if "disabilities" in data:
        record.disabilities = data["disabilities"]
    if "organ_donor" in data:
        record.organ_donor = data["organ_donor"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
