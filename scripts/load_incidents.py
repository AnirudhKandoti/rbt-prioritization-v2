from datetime import datetime, timezone, timedelta
from app.database import Base, engine, SessionLocal
from app.telemetry_ingest import upsert_module, add_incidents

Base.metadata.create_all(bind=engine)
db = SessionLocal()

m = upsert_module(db, "checkout", None, None)
now = datetime.now(timezone.utc)
incidents = [
    {"title":"Payment gateway timeout","severity":4,"started_at":(now - timedelta(days=3)).isoformat()},
    {"title":"DB saturation","severity":3,"started_at":(now - timedelta(days=9)).isoformat()},
    {"title":"Canary regression","severity":2,"started_at":(now - timedelta(days=12)).isoformat()},
]
add_incidents(db, m, incidents)
db.commit(); db.close()
print("Loaded sample incidents for checkout.")
