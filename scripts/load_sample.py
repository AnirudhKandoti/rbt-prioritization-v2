import random, datetime
from app.database import Base, engine, SessionLocal
from app.telemetry_ingest import upsert_module, add_events

Base.metadata.create_all(bind=engine)
db = SessionLocal()

mods = [("checkout","payments@acme.io","commerce"), ("auth","platform@acme.io","platform")]
def gen():
    return [
        {"kind":"error_rate","value":random.uniform(0.0,0.15)},
        {"kind":"change_frequency","value":random.randint(0,12)},
        {"kind":"code_churn","value":random.randint(50,1600)},
        {"kind":"complexity","value":random.uniform(0.2,0.85)},
        {"kind":"customer_impact","value":random.choice([0.3,0.6,0.8])},
        {"kind":"sla_breaches","value":random.choice([0,0,1])},
        {"kind":"test_flakiness","value":random.uniform(0.0,0.25)},
    ]

for name, owner, domain in mods:
    m = upsert_module(db, name, owner, domain)
    for d in range(14):
        day = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14-d)
        evs = gen()
        for e in evs:
            e["at"] = day.isoformat()
        add_events(db, m, evs)

db.commit(); db.close()
print("Loaded telemetry for modules:", [m[0] for m in mods])
