"""Ministry of Finance — manages tax records and declarations."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import FinanceRecord

app = FastAPI(title="Ministry of Finance", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-finance"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(FinanceRecord).filter(FinanceRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "tax_id": record.tax_id,
        "tax_status": record.tax_status,
        "annual_declarations": record.annual_declarations,
        "fines": record.fines,
        "company_ownerships": record.company_ownerships,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(FinanceRecord).filter(FinanceRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "tax_id" in data:
        record.tax_id = data["tax_id"]
    if "tax_status" in data:
        record.tax_status = data["tax_status"]
    if "annual_declarations" in data:
        record.annual_declarations = data["annual_declarations"]
    if "fines" in data:
        record.fines = data["fines"]
    if "company_ownerships" in data:
        record.company_ownerships = data["company_ownerships"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
