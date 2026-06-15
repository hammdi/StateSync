"""Ministry of Property — manages the land and property registry."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import PropertyRecord

app = FastAPI(title="Ministry of Property", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-property"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(PropertyRecord).filter(PropertyRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "properties": record.properties,
        "mortgages": record.mortgages,
        "land_registry": record.land_registry,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(PropertyRecord).filter(PropertyRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "properties" in data:
        record.properties = data["properties"]
    if "mortgages" in data:
        record.mortgages = data["mortgages"]
    if "land_registry" in data:
        record.land_registry = data["land_registry"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
