from dataclasses import dataclass

@dataclass
class RiskWeights:
    error_rate: float = 5.0
    change_frequency: float = 4.0
    code_churn: float = 3.0
    complexity: float = 2.0
    customer_impact: float = 4.0
    sla_breaches: float = 3.0
    test_flakiness: float = 2.0
    incident_count: float = 3.5
    incident_max_severity: float = 2.5
    incident_recency: float = 3.0

DEFAULT_WEIGHTS = RiskWeights()

NORMALIZATION_CAPS = {
    "error_rate": 0.2,
    "change_frequency": 14.0,
    "code_churn": 2000.0,
    "complexity": 1.0,
    "customer_impact": 1.0,
    "sla_breaches": 10.0,
    "test_flakiness": 0.5,
    "incident_count": 10.0,
    "incident_max_severity": 5.0,
    "incident_recency": 1.0,
}

BANDS = [("High", 70), ("Medium", 40), ("Low", 0)]
