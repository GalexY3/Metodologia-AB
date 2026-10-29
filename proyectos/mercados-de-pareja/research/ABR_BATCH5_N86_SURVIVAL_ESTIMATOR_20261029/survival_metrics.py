"""Pure-stdlib survival estimator for ESBM durations with administrative censoring.

NOT fitted to people. KM/RMST needs independent censoring assumptions and
followup support to horizon; mixed entry cohorts and risks may violate these.
Original frozen ESBM v2 script is not edited or silently re-run here.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable


def km_rmst(durations: Iterable[int], events: Iterable[int], horizon: int = 16) -> dict:
    """Discrete Kaplan-Meier restricted mean up to horizon, not unrestricted mean."""
    times = list(durations)
    flags = list(events)
    if not isinstance(horizon, int) or horizon < 2:
        raise ValueError("horizon must be an integer >=2")
    if not times or len(times) != len(flags):
        raise ValueError("times/events must be nonempty and equal length")
    if any(not isinstance(t, int) or isinstance(t, bool) or t < 1 or t > horizon for t in times):
        raise ValueError("all durations must be integers in [1,horizon]")
    if any(type(e) is not int or e not in (0, 1) for e in flags):
        raise ValueError("event flags must be native integers 0 or 1")
    if any(e and t == horizon for t, e in zip(times, flags)):
        raise ValueError("ESBM dissolutions only arise before end of horizon")
    if any(e == 0 for e in flags) and max(times) < horizon:
        raise ValueError("RMST not supported past last censoring time")

    deaths = Counter(t for t, e in zip(times, flags) if e == 1)
    censored = Counter(t for t, e in zip(times, flags) if e == 0)
    risk = len(times)
    survival = 1.0
    restricted_mean = 0.0
    for t in range(horizon):
        if t:
            d = deaths[t]
            c = censored[t]
            if d > risk or d + c > risk:
                raise AssertionError("risk-set underflow")
            if d:
                survival *= (risk - d) / risk
            risk -= d + c
        restricted_mean += survival

    completed = [t for t, e in zip(times, flags) if e]
    return {
        "horizon": horizon,
        "n": len(times),
        "events": len(completed),
        "censored": len(times) - len(completed),
        "rmst": restricted_mean,
        "completed_only_mean": sum(completed) / len(completed) if completed else None,
        "survival_at_horizon_minus_one": survival,
        "method": "discrete_Kaplan_Meier_RMST_conditional_on_independent_censoring",
    }


def from_esbm_histories(completed: Iterable[int], censored: Iterable[int], horizon: int = 16) -> dict:
    """Adapter for original ESBM arrays. Does not imply censoring ignorability."""
    a = list(completed)
    b = list(censored)
    return km_rmst(a + b, [1] * len(a) + [0] * len(b), horizon)
