from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.telemetry_ingest import upsert_module, add_events

def setup_module():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)

def test_ops_recommend_spikes():
    client = TestClient(app)
    db = SessionLocal()
    m = upsert_module(db, "auth", None, None)
    seq = [0.01,0.01,0.012,0.013,0.014,0.03]
    add_events(db, m, [{"kind":"error_rate","value":v} for v in seq])
    db.commit(); db.close()

    r = client.get("/ops/recommend")
    assert r.status_code == 200
    found = [x for x in r.json() if x["module_name"]=="auth"][0]
    assert found["spike_detected"] is True
    assert "error_rate" in found["suggested_thresholds"]
