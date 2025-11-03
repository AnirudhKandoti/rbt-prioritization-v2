from sqlalchemy.orm import Session
from datetime import datetime, timezone
from . import models

def _to_dt(val):
    """Accept None, datetime, or ISO string (with or without 'Z')."""
    if val is None:
        return datetime.now(timezone.utc)
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except Exception:
            pass
    # Fallback: now (UTC)
    return datetime.now(timezone.utc)

def upsert_module(db: Session, name: str, owner: str | None, domain: str | None):
    m = db.query(models.Module).filter(models.Module.name == name).one_or_none()
    if not m:
        m = models.Module(name=name, owner=owner, domain=domain)
        db.add(m)
        db.flush()
    else:
        if owner:
            m.owner = owner
        if domain:
            m.domain = domain
    return m

def add_events(db: Session, module: models.Module, events: list[dict]):
    for e in events:
        at = _to_dt(e.get("at"))
        ev = models.TelemetryEvent(
            module_id=module.id,
            kind=e["kind"],
            value=float(e["value"]),
            at=at,
        )
        db.add(ev)
    db.flush()

def add_incidents(db: Session, module: models.Module, incidents: list[dict]):
    for inc in incidents:
        started = _to_dt(inc.get("started_at"))
        resolved = _to_dt(inc.get("resolved_at"))
        db.add(
            models.Incident(
                module_id=module.id,
                title=inc["title"],
                severity=int(inc.get("severity", 3)),
                started_at=started,
                resolved_at=resolved,
                root_cause=inc.get("root_cause"),
            )
        )
    db.flush()
