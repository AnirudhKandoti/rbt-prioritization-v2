from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    owner = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    last_change_at = Column(DateTime(timezone=True), nullable=True)

    telemetry = relationship("TelemetryEvent", back_populates="module", cascade="all, delete-orphan")
    risks = relationship("RiskSnapshot", back_populates="module", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="module", cascade="all, delete-orphan")

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id"), index=True, nullable=False)
    kind = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)
    at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    module = relationship("Module", back_populates="telemetry")

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    severity = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    root_cause = Column(String, nullable=True)

    module = relationship("Module", back_populates="incidents")

class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id"), index=True, nullable=False)
    score = Column(Float, index=True, nullable=False)
    band = Column(String, index=True, nullable=False)
    contributions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    module = relationship("Module", back_populates="risks")
    __table_args__ = (UniqueConstraint("module_id", "created_at", name="uq_module_risk_time"),)
