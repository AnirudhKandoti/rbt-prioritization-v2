from typing import Dict, Tuple, List
from .config import DEFAULT_WEIGHTS, NORMALIZATION_CAPS, BANDS

def _clip(v: float, cap: float) -> float:
    return max(0.0, min(v, cap))

def _norm(v: float, cap: float) -> float:
    return _clip(v, cap) / cap if cap > 0 else 0.0

def compute_score(features: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    w = DEFAULT_WEIGHTS.__dict__
    tot = sum(w.values())
    contribs: Dict[str, float] = {}
    acc = 0.0
    for k, wk in w.items():
        v = features.get(k, 0.0)
        c = 100.0 * wk * _norm(v, NORMALIZATION_CAPS.get(k, 1.0)) / tot
        contribs[k] = round(c, 2)
        acc += wk * _norm(v, NORMALIZATION_CAPS.get(k, 1.0))
    score = 100.0 * acc / tot
    return round(score, 2), contribs

def band_for(score: float) -> str:
    for name, thr in BANDS:
        if score >= thr:
            return name
    return "Low"

def make_reasons(f: Dict[str, float]) -> List[str]:
    reasons = []
    if f.get("error_rate",0)>0.05: reasons.append("Error rate above 5%.")
    if f.get("change_frequency",0)>7: reasons.append("High change frequency (>7).")
    if f.get("code_churn",0)>800: reasons.append("Heavy code churn (>800 LOC).")
    if f.get("complexity",0)>0.6: reasons.append("High complexity (>0.6).")
    if f.get("customer_impact",0)>0.7: reasons.append("High customer impact.")
    if f.get("sla_breaches",0)>=1: reasons.append("Recent SLA breach(es).")
    if f.get("test_flakiness",0)>0.15: reasons.append("Elevated test flakiness (>15%).")
    if f.get("incident_count",0)>=3: reasons.append("Multiple incidents recently (>=3).")
    if f.get("incident_max_severity",0)>=4: reasons.append("Recent high-severity incident (sev4+).")
    if f.get("incident_recency",0)>0.6: reasons.append("Recent incident cluster (recency-weighted).")
    if not reasons: reasons.append("No standout risk drivers; routine monitoring.")
    return reasons
