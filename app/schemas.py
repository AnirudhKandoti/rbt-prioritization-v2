from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class TelemetryPoint(BaseModel):
    kind: str
    value: float
    at: Optional[datetime] = None

class TelemetryIngest(BaseModel):
    module_name: str
    owner: Optional[str] = None
    domain: Optional[str] = None
    events: List[TelemetryPoint]

class IncidentIngest(BaseModel):
    module_name: str
    incidents: List[dict]

class RiskOut(BaseModel):
    module_name: str
    score: float
    band: str
    contributions: Dict[str, float]
    reasons: List[str]

class PriorityOut(BaseModel):
    items: List[RiskOut]

class OpsRecommendation(BaseModel):
    module_name: str
    spike_detected: bool
    suggested_thresholds: Dict[str, float]
    runbook_steps: List[str]
