# app/routers/priorities.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import datetime, timezone

from ..database import get_db
from .. import models, schemas
from ..prioritizer import compute_score, band_for, make_reasons

router = APIRouter(prefix="/priorities", tags=["priorities"])

def _as_utc_aware(dt):
    """Normalize DB datetimes to UTC-aware so we can subtract safely."""
    if dt is None:
        return None
    if isinstance(dt, str):
        try:
            return datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _aggregate_features(db: Session, module_id: int) -> dict:
    # Averages for all telemetry kinds
    rows = db.execute(
        select(models.TelemetryEvent.kind, func.avg(models.TelemetryEvent.value))
        .where(models.TelemetryEvent.module_id == module_id)
        .group_by(models.TelemetryEvent.kind)
    ).all()
    feats = {k: float(v or 0.0) for k, v in rows}

    # Incident features
    inc_count = db.query(models.Incident).filter(models.Incident.module_id == module_id).count()
    max_sev = (
        db.query(func.max(models.Incident.severity))
        .filter(models.Incident.module_id == module_id)
        .scalar()
        or 0
    )
    last = (
        db.query(func.max(models.Incident.started_at))
        .filter(models.Incident.module_id == module_id)
        .scalar()
    )
    last = _as_utc_aware(last)
    if last:
        days = (datetime.now(timezone.utc) - last).total_seconds() / 86400.0
        recency = max(0.0, min(1.0, 1.0 / (1.0 + days / 7.0)))
    else:
        recency = 0.0

    feats.update(
        {
            "incident_count": float(inc_count),
            "incident_max_severity": float(max_sev),
            "incident_recency": float(recency),
        }
    )

    # Ensure all expected telemetry keys exist
    for k in [
        "error_rate",
        "change_frequency",
        "code_churn",
        "complexity",
        "customer_impact",
        "sla_breaches",
        "test_flakiness",
    ]:
        feats.setdefault(k, 0.0)

    return feats

@router.get("", response_model=schemas.PriorityOut)
def get_priorities(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    modules = db.query(models.Module).order_by(models.Module.name).limit(limit).all()
    items = []
    for m in modules:
        feats = _aggregate_features(db, m.id)
        score, contribs = compute_score(feats)
        items.append(
            {
                "module_name": m.name,
                "score": score,
                "band": band_for(score),
                "contributions": contribs,
                "reasons": make_reasons(feats),
            }
        )
    items.sort(key=lambda x: x["score"], reverse=True)
    return {"items": items}

# Also accept /priorities/ (trailing slash)
@router.get("/", response_model=schemas.PriorityOut, include_in_schema=False)
def get_priorities_slash(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    return get_priorities(limit=limit, db=db)
