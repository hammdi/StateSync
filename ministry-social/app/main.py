"""Ministry of Social Affairs — manages social security, retirement, and benefits."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import SocialRecord

app = FastAPI(title="Ministry of Social Affairs", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-social"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(SocialRecord).filter(SocialRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "social_number": record.social_number,
        "employment_history": record.employment_history,
        "pension_points": record.pension_points,
        "contributions": record.contributions,
        "benefits": record.benefits,
        "unemployment_status": record.unemployment_status,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(SocialRecord).filter(SocialRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "social_number" in data:
        record.social_number = data["social_number"]
    if "employment_history" in data:
        record.employment_history = data["employment_history"]
    if "pension_points" in data:
        record.pension_points = data["pension_points"]
    if "contributions" in data:
        record.contributions = data["contributions"]
    if "benefits" in data:
        record.benefits = data["benefits"]
    if "unemployment_status" in data:
        record.unemployment_status = data["unemployment_status"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
