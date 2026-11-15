"""Independent convolution of frozen voting laws; no trainer/evaluator import."""
from pathlib import Path
import hashlib
import json
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
ROOT = R/'V198_VOTING_EXPECTED_DRIFT'


def main():
    output = R/'V198_NUMPY_FINAL_AUDIT.json'
    assert not output.exists()
    registration = json.loads((R/'V198_EXPECTED_DRIFT_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    for path, sha in dict(registration['source_sha256'], **registration['binary_parent_sha256']).items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    summary = json.loads((ROOT/'SUMMARY.json').read_text(encoding='utf-8'))
    checks = []
    for run in summary['results']:
        k, rule, arm = run['k'], run['rule'], run['arm']
        n = k-1
        h = n if rule == 'UNANIMITY' else n//2+1
        losses = np.empty((32, 20, n))
        for w in range(32):
            seed = int.from_bytes(hashlib.sha256(f'V195-private-stakes-world-{k}-{w}'.encode()).digest()[:8], 'little')
            losses[w] = np.where(np.random.Generator(np.random.Philox(seed)).random((20, n)) < .5, 1., 7.)
        values = []
        for step in [0, 8000]:
            path = ROOT/f'k{k}_{rule}_{arm}_step{step}.npz'
            q = np.load(path)['Q']
            if step == 0:
                parent = np.load(R/f'V195_CORRELATED_EXPLORATION/V195_k{k}_{rule}_W32_G20_T8000.npz')['JOINT_SIGNAL_PULSE_10']
                assert np.array_equal(q, parent)
            # Independently written CDF and scalar polynomial convolution.
            delta = (q[..., 1]-q[..., 0])/1e-12
            yes = np.empty_like(delta)
            yes[delta <= -1] = 0.
            yes[delta >= 1] = 1.
            lower = (delta > -1) & (delta < 0)
            upper = (delta >= 0) & (delta < 1)
            yes[lower] = (delta[lower]+1)**2/2
            yes[upper] = 1-(1-delta[upper])**2/2
            per_world = []
            for w in range(32):
                group_values = []
                for g in range(20):
                    tails = []
                    for positive in [.8, .2]:
                        probabilities = positive*yes[w, g, :, 1]+(1-positive)*yes[w, g, :, 0]
                        polynomial = np.array([1.])
                        for p in probabilities:
                            polynomial = np.convolve(polynomial, np.array([1-p, p]))
                        tails.append(float(polynomial[h:].sum()))
                    group_values.append(.6*tails[0]-.4*losses[w, g].mean()*tails[1])
                per_world.append(float(np.mean(group_values)))
            saved = next(row for row in run['history'] if row['step'] == step)
            for w, value in enumerate(per_world):
                error = abs(value-saved['world_welfare'][w])
                checks.append(dict(k=k, rule=rule, arm=arm, step=step, world=w,
                                   error=error, passed=bool(error < 2e-11)))
            values.append(float(np.mean(per_world)))
        assert abs(values[-1]/values[0]-run['final_retention_ratio']) < 1e-10
        assert run['meets75percent'] == bool(values[-1]/values[0] >= .75)
    counts = {arm: sum(r['meets75percent'] for r in summary['results'] if r['arm'] == arm)
              for arm in ['MEAN_EPS08', 'MEAN_EPS00']}
    assert counts == summary['retention75_counts']
    result = dict(metric_checks=len(checks), failures=[c for c in checks if not c['passed']],
        maximum_error=max(c['error'] for c in checks), independent_convolution_engine=True,
        source_and_parent_hashes_unchanged=True, original_parent_Qs_preserved_in_all_arms=True,
        primary_counts=counts, independent_new_training_roots=0, checks=checks)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    assert not result['failures']
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
