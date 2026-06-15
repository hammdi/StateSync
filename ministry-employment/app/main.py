"""Ministry of Employment — manages employment status and work contracts."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import EmploymentRecord

app = FastAPI(title="Ministry of Employment", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-employment"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(EmploymentRecord).filter(EmploymentRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "employment_status": record.employment_status,
        "current_employer": record.current_employer,
        "contracts": record.contracts,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(EmploymentRecord).filter(EmploymentRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "employment_status" in data:
        record.employment_status = data["employment_status"]
    if "current_employer" in data:
        record.current_employer = data["current_employer"]
    if "contracts" in data:
        record.contracts = data["contracts"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
