"""Ministry of Commerce — manages business registrations."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import CommerceRecord

app = FastAPI(title="Ministry of Commerce", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-commerce"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(CommerceRecord).filter(CommerceRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "businesses": record.businesses,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(CommerceRecord).filter(CommerceRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "businesses" in data:
        record.businesses = data["businesses"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
