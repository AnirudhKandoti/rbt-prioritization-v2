from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from ..telemetry_ingest import upsert_module, add_incidents

router = APIRouter(prefix="/ingest", tags=["incidents"])

@router.post("/incidents")
def ingest_incidents(payload: schemas.IncidentIngest, db: Session = Depends(get_db)):
    m = upsert_module(db, payload.module_name, None, None)
    add_incidents(db, m, payload.incidents)
    db.commit()
    return {"status":"ok","module":m.name,"incidents":len(payload.incidents)}
