from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models, schemas
from ..utils.spikes import is_spike

router = APIRouter(prefix="/ops", tags=["ops"])

def _series(db: Session, module_id: int, kind: str):
    rows = db.execute(select(models.TelemetryEvent.value).where(models.TelemetryEvent.module_id==module_id, models.TelemetryEvent.kind==kind).order_by(models.TelemetryEvent.at.asc())).all()
    return [float(r[0]) for r in rows]

def _runbook(name: str):
    steps = ["Check latest deploys/flags", "Inspect error logs and traces", "Check dependencies", "Adjust canary %, scale up"]
    if "auth" in name: steps.insert(0,"Lower login rate limits temporarily")
    if "checkout" in name: steps.insert(0,"Failover payment provider if persists")
    return steps

@router.get("/recommend", response_model=list[schemas.OpsRecommendation])
def recommend(db: Session = Depends(get_db)):
    modules = db.query(models.Module).all()
    res = []
    for m in modules:
        series = _series(db, m.id, "error_rate")
        spike = is_spike(series)
        thresholds = {}
        if spike and series:
            thresholds["error_rate"] = max(0.01, round(series[-1]*0.8,3))
        res.append({"module_name": m.name, "spike_detected": bool(spike), "suggested_thresholds": thresholds, "runbook_steps": _runbook(m.name) if spike else ["No spike detected."]})
    return res
