"""M042: paired, cluster-level comparison of AB experimental variants.

No model execution, no graded truth and no causal effects are claimed by this module.
A benchmark report is descriptive unless preregistration and experimental assumptions hold.
"""
from __future__ import annotations

import itertools
import math
import random
from collections import defaultdict

from .core import ABError, require

ALLOWED_STATUSES = ("success", "failed", "timeout")


def _validated_rows(rows: list[dict]) -> None:
    if not rows:
        raise ABError("No benchmark rows")
    seen = set()
    for r in rows:
        require(r, {"case_id": str, "arm": str, "replicate": int,
                    "status": str, "blind_id": str, "model_version": str,
                    "budget_id": str}, "benchmark_row")
        for field in ("score", "cost_seconds"):
            if (field not in r or isinstance(r[field], bool)
                    or not isinstance(r[field], (int, float))
                    or not math.isfinite(r[field])):
                raise ABError(f"{field} must be a finite number")
        if not (0 <= r["score"] <= 1):
            raise ABError("score must be in [0,1]")
        if r["cost_seconds"] < 0:
            raise ABError("cost_seconds cannot be negative")
        if r["status"] not in ALLOWED_STATUSES:
            raise ABError("Unsupported run status")
        if r["status"] != "success" and r["score"] != 0:
            raise ABError("Failed/timeout run must have a score of 0")
        if not r["case_id"] or not r["arm"] or not r["blind_id"]:
            raise ABError("Missing case/arm/blind id")
        key = (r["case_id"], r["arm"], r["replicate"])
        if key in seen:
            raise ABError(f"Duplicate run: {key}")
        seen.add(key)


def _average(values: list[float]) -> float:
    return sum(values) / len(values)


def _bootstrap_ci(differences: list[float], seed: int, draws: int) -> list[float]:
    rng = random.Random(seed)
    n = len(differences)
    means = sorted(_average([differences[rng.randrange(n)] for _ in range(n)])
                   for _ in range(draws))
    return [means[int(.025 * (draws - 1))],
            means[int(.975 * (draws - 1))]]


def _signflip_p(differences: list[float], seed: int, draws: int) -> float:
    n = len(differences)
    target = abs(_average(differences))
    if n <= 16:
        signed = itertools.product((-1, 1), repeat=n)
        extreme = sum(abs(_average([sgn * x for sgn, x in zip(signs, differences)]))
                      >= target - 1e-12 for signs in signed)
        return extreme / (2 ** n)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(draws):
        test = abs(_average([(1 if rng.getrandbits(1) else -1) * x
                             for x in differences]))
        extreme += test >= target - 1e-12
    return (extreme + 1) / (draws + 1)


def compare(rows: list[dict], baseline: str = "baseline", candidate: str = "ab",
            seed: int = 20261114, draws: int = 2000) -> dict:
    _validated_rows(rows)
    if baseline == candidate:
        raise ABError("Two different conditions required")
    if draws < 100:
        raise ABError("At least 100 bootstrap draws")
    subset = [r for r in rows if r["arm"] in (baseline, candidate)]
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in subset:
        grouped[(r["case_id"], r["arm"])].append(r)
    cases_a = {case for case, arm in grouped if arm == baseline}
    cases_b = {case for case, arm in grouped if arm == candidate}
    if not cases_a or cases_a != cases_b:
        raise ABError("Paired arms must have the same case IDs")
    cases = sorted(cases_a)
    unequal_replicates = []
    differences = []
    per_case = []
    for case in cases:
        a, b = grouped[(case, baseline)], grouped[(case, candidate)]
        if len(a) != len(b):
            unequal_replicates.append(case)
        mean_a, mean_b = _average([x["score"] for x in a]), _average([x["score"] for x in b])
        differences.append(mean_b - mean_a)
        per_case.append({"case_id": case, "baseline_mean": mean_a,
                         "candidate_mean": mean_b, "difference": mean_b - mean_a})
    if unequal_replicates:
        raise ABError("Unequal replicate counts for " + ", ".join(unequal_replicates))
    models = {r["model_version"] for r in subset}
    budgets = {r["budget_id"] for r in subset}
    blind_collisions = len({r["blind_id"] for r in subset}) != len(subset)
    warnings = []
    if len(models) > 1:
        warnings.append("MODEL_VERSION_MISMATCH")
    if len(budgets) > 1:
        warnings.append("BUDGET_SPECIFICATION_MISMATCH")
    if blind_collisions:
        warnings.append("BLIND_IDS_NOT_UNIQUE")
    if len(cases) < 30:
        warnings.append("SMALL_EXPLORATORY_PILOT")
    if not warnings:
        warnings.append("Design and scorer validity still require independent audit")
    costs = {arm: _average([r["cost_seconds"] for r in subset if r["arm"] == arm])
             for arm in (baseline, candidate)}
    return {
        "schema": "AB-META-EVAL-0.1",
        "baseline": baseline, "candidate": candidate,
        "n_independent_cases": len(cases),
        "n_trajectories": len(subset),
        "difference_candidate_minus_baseline": _average(differences),
        "bootstrap_95_percentile_ci": _bootstrap_ci(differences, seed, draws),
        "paired_signflip_p_two_sided": _signflip_p(differences, seed, draws),
        "cost_seconds_mean_per_trajectory": costs,
        "per_case": per_case, "warnings": warnings,
        "interpretation": (
            "Statistical calculation only; causal claims require randomized, parity-controlled "
            "runs, blinded calibrated grading, an unreused holdout and independent task clusters."
        ),
    }


def compare_ablations(rows: list[dict], baseline: str = "baseline",
                      seed: int = 20261114, draws: int = 2000) -> dict:
    candidates = sorted({r["arm"] for r in rows} - {baseline})
    if not candidates:
        raise ABError("At least one candidate arm needed")
    return {
        "comparisons": {arm: compare(rows, baseline, arm, seed, draws)
                        for arm in candidates},
        "multiplicity_note": (
            "Several comparisons are exploratory; do not declare confirmatory discoveries "
            "using their unadjusted p-values without a prespecified multiplicity plan."
        ),
    }
