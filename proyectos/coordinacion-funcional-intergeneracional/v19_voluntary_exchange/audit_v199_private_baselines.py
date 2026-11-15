"""Independent convolution, memory invariants and private-return accounting.

Does not import the trainer, its probability evaluator or Poisson-binomial code.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
ROOT = R/'V199_PRIVATE_BASELINES'
NAMES = ['IQL_JITTER', 'IQL_EXACT', 'IQL_SLOW', 'HYSTERETIC', 'RUNNING_MEAN', 'LMRL2', 'FROZEN', 'IQL_MIN']


def probability(q, temp, method, epsilon, native):
    difference = q[..., 1]-q[..., 0]
    p = (difference > 0).astype(float)+.5*(difference == 0)
    if method == 0:
        d = difference/1e-12
        p = np.ones_like(d)
        p[d <= -1] = 0.
        low = (d > -1) & (d < 0)
        high = (d >= 0) & (d < 1)
        p[low] = (1+d[low])**2/2
        p[high] = 1-(1-d[high])**2/2
    if native and method == 5:
        t = (temp[..., 0]+temp[..., 1])/2
        use = t >= 2
        d = difference[use]/t[use]
        # Numerically stable two-action softmax independently formulated.
        positive = d >= 0
        values = np.empty_like(d)
        values[positive] = 1/(1+np.exp(-d[positive]))
        z = np.exp(d[~positive])
        values[~positive] = z/(1+z)
        p[use] = values
    elif native and method != 6:
        p = (1-epsilon)*p+epsilon/2
    return p


def world_values(q, temp, losses, method, epsilon, accuracy, quorum, native):
    yes = probability(q, temp, method, epsilon, native)
    by_world = []
    for w in range(32):
        payoffs = []
        for g in range(20):
            approval = []
            for positive in [accuracy, 1-accuracy]:
                probabilities = positive*yes[w, g, :, 1]+(1-positive)*yes[w, g, :, 0]
                polynomial = np.array([1.])
                for prob in probabilities:
                    polynomial = np.convolve(polynomial, [1-prob, prob])
                assert abs(polynomial.sum()-1) < 1e-12
                approval.append(float(polynomial[quorum:].sum()))
            payoffs.append(.6*approval[0]-.4*losses[w, g]*approval[1])
        payoffs = np.array(payoffs)
        low, high = losses[w] == 1, losses[w] == 7
        by_world.append([float(payoffs.mean()), float(payoffs[low].mean()), float(payoffs[high].mean())])
    return np.array(by_world)


def main():
    output = R/'V199_PRIVATE_BASELINES_AUDIT.json'
    assert not output.exists() and (ROOT/'SUMMARY.json').exists()
    registration = json.loads((R/'V199_PRIVATE_BASELINES_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    for path, sha in dict(registration['source_sha256'], **registration['binary_parent_sha256']).items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    all_checks, memory_checks, return_checks, summaries = [], [], [], []
    for cohort in ['MAINTENANCE', 'FORMATION']:
        for k in [4, 8, 12]:
            for rule in ['UNANIMITY', 'MAJORITY']:
                folder = ROOT/f'{cohort}_k{k}_{rule}'
                context = np.load(folder/'CONTEXT.npz')
                losses, ids = context['losses'], context['method_ids']
                quorum = k-1 if rule == 'UNANIMITY' else k//2
                raw = json.loads((folder/'SUMMARY.json').read_text(encoding='utf-8'))
                initial = np.load(folder/'checkpoint_0.npz')['Q']
                runs = {r['method']: r for r in raw['runs']}
                derived_running_rewards = {}
                for step in [0, 4000, 8000, 12000]:
                    saved = np.load(folder/f'checkpoint_{step}.npz')
                    q, count, temperature = saved['Q'], saved['counts'], saved['temperatures']
                    assert int(saved['step']) == step
                    assert np.isfinite(q).all() and q.min() >= -7.0000000001 and q.max() <= 1.0000000001
                    for j, method in enumerate(ids):
                        assert np.all(count[j].sum((-1, -2)) == (0 if method == 6 else step))
                        untouched = count[j] == 0
                        assert np.array_equal(q[j][untouched], initial[j][untouched])
                        if method == 5:
                            assert np.allclose(temperature[j], 50*np.power(.995, count[j]), rtol=2e-12, atol=1e-300)
                        else:
                            assert np.all(temperature[j] == 50.)
                        if method == 6:
                            assert np.array_equal(q[j], initial[j])
                        memory_checks.append(dict(cohort=cohort, k=k, rule=rule, step=step, method=NAMES[method],
                            counts_and_unvisited_parameters_valid=True, temperatures_valid=True))
                        if method == 4:
                            # A running mean must encode the sum of actual integer
                            # private returns, not peer-average rewards or labels.
                            totals = (9+count[j])*q[j]-9*initial[j]
                            error = float(np.max(np.abs(totals-np.rint(totals))))
                            assert error < 2e-7
                            derived_running_rewards[step] = totals.sum((-1, -2))
                        if step not in [0, 8000, 12000]:
                            continue
                        epsilon = .3-.22*min(step, 6000)/6000 if cohort == 'FORMATION' and step < 8000 else .08
                        accuracy = .8 if step <= 8000 else .2
                        row = next(r for r in runs[NAMES[method]]['history'] if r['step'] == step)
                        for native in [False, True]:
                            values = world_values(q[j], temperature[j], losses, method, epsilon, accuracy, quorum, native)
                            fields = ['native_world_welfare'] if native else ['greedy_world_welfare', 'greedy_world_low_payoff', 'greedy_world_high_payoff']
                            for column, field in enumerate(fields):
                                for w, value in enumerate(values[:, column]):
                                    error = abs(value-row[field][w])
                                    all_checks.append(dict(cohort=cohort, k=k, rule=rule, method=NAMES[method],
                                        step=step, field=field, world=w, error=error, passed=bool(error < 2e-11)))
                        if step == 8000:
                            summaries.append(dict(cohort=cohort, k=k, rule=rule, method=NAMES[method],
                                mean_welfare=row['greedy_mean_welfare'], low_payoff=row['greedy_low_payoff'], high_payoff=row['greedy_high_payoff']))
                running = runs['RUNNING_MEAN']
                for phase, start, end in [(0, 0, 8000), (1, 8000, 12000)]:
                    realized = (derived_running_rewards[end]-derived_running_rewards[start])/(end-start)
                    per_world = realized.mean((1, 2))
                    record = running['observed_private_payoffs'][phase]
                    error = float(np.max(np.abs(per_world-np.array(record['world_welfare']))))
                    assert error < 2e-9
                    return_checks.append(dict(cohort=cohort, k=k, rule=rule, phase=phase,
                        running_mean_encodes_observed_private_returns=True, maximum_world_error=error))
    failures = [c for c in all_checks if not c['passed']]
    result = dict(independent_probability_and_convolution_engine=True, metric_checks=len(all_checks),
        failures=failures, maximum_error=max(c['error'] for c in all_checks),
        private_memory_checks=len(memory_checks), private_running_return_checks=len(return_checks),
        memory_checks=memory_checks, running_return_checks=return_checks, checks=all_checks,
        source_and_parent_hashes_unchanged=True, endpoints_and_primary_snapshot_valid=True,
        summaries=summaries, external_scientific_replication_claimed=False)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    assert not failures
    print(json.dumps({k: v for k, v in result.items() if k not in
        ['checks', 'memory_checks', 'running_return_checks', 'summaries']}), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
