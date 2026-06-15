"""Ministry of Education — manages diplomas and equivalence records."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import EducationRecord

app = FastAPI(title="Ministry of Education", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-education"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(EducationRecord).filter(EducationRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "diplomas": record.diplomas,
        "equivalences": record.equivalences,
        "scholarships": record.scholarships,
        "current_enrollment": record.current_enrollment,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(EducationRecord).filter(EducationRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "diplomas" in data:
        record.diplomas = data["diplomas"]
    if "equivalences" in data:
        record.equivalences = data["equivalences"]
    if "scholarships" in data:
        record.scholarships = data["scholarships"]
    if "current_enrollment" in data:
        record.current_enrollment = data["current_enrollment"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
