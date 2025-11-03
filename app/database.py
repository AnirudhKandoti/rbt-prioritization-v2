from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os, argparse

DB_PATH = os.getenv("RBT_DB_PATH", "rbt.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    from .models import Module, TelemetryEvent, RiskSnapshot, Incident
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    if args.init:
        Base.metadata.create_all(bind=engine)
        print("Initialized DB:", DB_PATH)
