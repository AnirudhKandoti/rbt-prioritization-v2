# app/routers/modules.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..prioritizer import compute_score, band_for, make_reasons
from datetime import datetime, timezone

router = APIRouter(prefix="/modules", tags=["modules"])

def _as_utc_aware(dt):
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

@router.get("/{name}")
def module_detail(name: str, db: Session = Depends(get_db)):
    m = db.query(models.Module).filter(models.Module.name == name).one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")

    feats: dict[str, float] = {}
    for ev in m.telemetry:
        feats.setdefault(ev.kind, []).append(ev.value)
    feats = {k: sum(v)/len(v) for k, v in feats.items()}

    count = len(m.incidents)
    max_sev = max([i.severity for i in m.incidents], default=0)

    if m.incidents:
        last = max(i.started_at for i in m.incidents)
        last = _as_utc_aware(last)
        days = (datetime.now(timezone.utc) - last).total_seconds() / 86400.0
        recency = max(0.0, min(1.0, 1.0 / (1.0 + days / 7.0)))
    else:
        recency = 0.0

    feats.update({
        "incident_count": float(count),
        "incident_max_severity": float(max_sev),
        "incident_recency": float(recency),
    })

    score, contribs = compute_score(feats)
    band = band_for(score)
    reasons = make_reasons(feats)

    return {
        "module": {"name": m.name, "owner": m.owner, "domain": m.domain},
        "features": feats,
        "score": score,
        "band": band,
        "contributions": contribs,
        "reasons": reasons,
    }
