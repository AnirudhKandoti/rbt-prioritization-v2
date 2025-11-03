from typing import List
import statistics as stats

def ewma(values: List[float], alpha: float = 0.3) -> float:
    if not values:
        return 0.0
    s = values[0]
    for v in values[1:]:
        s = alpha * v + (1 - alpha) * s
    return s

def is_spike(values: List[float], k: float = 3.0) -> bool:
    if len(values) < 5:
        return False
    m = ewma(values[:-1])
    resid = [abs(v - m) for v in values[:-1]]
    if len(resid) < 3:
        return False
    mu = stats.mean(resid)
    sigma = stats.pstdev(resid) or 1e-6
    last = abs(values[-1] - m)
    return last > (mu + k * sigma)
