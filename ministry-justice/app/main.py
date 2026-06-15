"""Ministry of Justice — manages criminal records."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import JusticeRecord

app = FastAPI(title="Ministry of Justice", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ministry-justice"}


@app.get("/data/{cin}")
async def get_record(cin: str, db: Session = Depends(get_db)):
    record = db.query(JusticeRecord).filter(JusticeRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "cin": record.cin,
        "criminal_record": record.criminal_record,
        "cases": record.cases,
        "sentences": record.sentences,
        "restrictions": record.restrictions,
    }


@app.put("/data/{cin}")
async def update_record(cin: str, data: dict, db: Session = Depends(get_db)):
    record = db.query(JusticeRecord).filter(JusticeRecord.cin == cin).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if "criminal_record" in data:
        record.criminal_record = data["criminal_record"]
    if "cases" in data:
        record.cases = data["cases"]
    if "sentences" in data:
        record.sentences = data["sentences"]
    if "restrictions" in data:
        record.restrictions = data["restrictions"]
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "updated", "cin": cin}
