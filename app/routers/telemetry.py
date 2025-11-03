from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from ..telemetry_ingest import upsert_module, add_events

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/telemetry")
def ingest_telemetry(payload: schemas.TelemetryIngest, db: Session = Depends(get_db)):
    m = upsert_module(db, payload.module_name, payload.owner, payload.domain)
    add_events(db, m, [e.dict() for e in payload.events])
    db.commit()
    return {"status":"ok","module":m.name}
