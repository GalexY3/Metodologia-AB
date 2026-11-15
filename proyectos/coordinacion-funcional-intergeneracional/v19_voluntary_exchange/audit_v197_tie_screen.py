"""Preserved initial screening script; the comprehensive V197 audit supersedes it."""
from pathlib import Path
import hashlib
import json
import numpy as np

B = Path(__file__).resolve().parent
rows = []
files = list((B/'results/V195_CORRELATED_EXPLORATION').glob('*.npz'))
files += list((B/'results/V196_POST_PULSE_PLASTICITY').glob('*.npz'))
for path in files:
    data = np.load(path)
    for arm in data.files:
        q = data[arm]
        d = q[..., 1]-q[..., 0]
        z = np.clip(d/1e-12, -1, 1)
        actual = np.where(z < 0, .5*(1+z)**2, 1-.5*(1-z)**2)
        evaluated = np.where(d > 1e-12, 1., np.where(d < -1e-12, 0., .5))
        diff = np.abs(actual-evaluated)
        rows.append(dict(file=path.relative_to(B).as_posix(), arm=arm, states=int(d.size),
            nonzero_policy_discrepancies=int((diff > 1e-12).sum()), max_policy_discrepancy=float(diff.max()),
            mean_policy_discrepancy=float(diff.mean()), source_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
out = B/'results/V197_TIE_PROBABILITY_SCREEN.json'
assert not out.exists()
out.write_text(json.dumps(dict(new_training_executed=False,
    explicit_issue='Adding independent uniform action jitters of width 1e-12 produces a triangular CDF inside near ties, whereas existing p_yes uses probability .5 there.',
    rows=rows), indent=2), encoding='utf-8')
print(json.dumps(dict(arrays=len(rows), states=sum(r['states'] for r in rows),
    affected_arrays=sum(r['nonzero_policy_discrepancies'] > 0 for r in rows),
    largest_discrepancy=max(r['max_policy_discrepancy'] for r in rows))), flush=True)
