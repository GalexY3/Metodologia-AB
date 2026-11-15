"""Recompute frozen-voting values using the trainer's actual tie-jitter law.

The old evaluators use probability1/2 throughout a tolerance interval. Adding
two independent uniform jitters instead gives a triangular CDF there. Original
training data and prior outputs are preserved. This audit does no new training.
"""
from pathlib import Path
import hashlib
import itertools
import json
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B / 'results'
ETA = 1e-12
W, G = 32, 20


def yes_probability(q, actual=True):
    delta = q[..., 1] - q[..., 0]
    if not actual:
        return np.where(delta > ETA, 1., np.where(delta < -ETA, 0., .5))
    z = np.clip(delta/ETA, -1., 1.)
    return np.where(z < 0, .5*(1+z)**2, 1-.5*(1-z)**2)


def population(k):
    losses = np.empty((W, G, k-1))
    for w in range(W):
        seed = int.from_bytes(hashlib.sha256(f'V195-private-stakes-world-{k}-{w}'.encode()).digest()[:8], 'little')
        rng = np.random.Generator(np.random.Philox(seed))
        losses[w] = np.where(rng.random((G, k-1)) < .5, 1., 7.)
    return losses


def tail(probabilities, threshold):
    n = probabilities.shape[-1]
    dp = np.zeros(probabilities.shape[:-1]+(n+1,))
    dp[..., 0] = 1.
    for i in range(n):
        old = dp.copy()
        prob = probabilities[..., i, None]
        dp[..., 0] = old[..., 0]*(1-prob[..., 0])
        dp[..., 1:] = old[..., 1:]*(1-prob)+old[..., :-1]*prob
    assert np.max(np.abs(dp.sum(-1)-1)) < 2e-12
    return dp[..., threshold:].sum(-1)


def evaluate(q, losses, threshold, arm, actual):
    if arm == 'ORACLE_STATE':
        return np.full(W, .6), np.ones((W, G)), np.zeros((W, G))
    if arm == 'SIGNAL_FOLLOW_CONTROL':
        probabilities_good = np.full(losses.shape, .8)
        probabilities_bad = np.full(losses.shape, .2)
    else:
        yes = yes_probability(q, actual)
        probabilities_good = .2*yes[..., 0]+.8*yes[..., 1]
        probabilities_bad = .8*yes[..., 0]+.2*yes[..., 1]
    good, bad = tail(probabilities_good, threshold), tail(probabilities_bad, threshold)
    welfare = .6*good-.4*losses.mean(-1)*bad
    return welfare.mean(1), good, bad


def technical():
    ratios = np.array([-2., -1., -.5, 0., .5, 1., 2.])
    values = np.stack([np.zeros_like(ratios), ratios*ETA], axis=-1)
    expected = np.array([0., 0., .125, .5, .875, 1., 1.])
    assert np.array_equal(yes_probability(values), expected)
    rng = np.random.default_rng(197553)
    max_probability_error, max_tail_error = 0., 0.
    for _ in range(20):
        delta = rng.uniform(-1.2, 1.2)*ETA
        reference = float(yes_probability(np.array([0., delta])))
        observed = float((delta+ETA*rng.random(200000) > ETA*rng.random(200000)).mean())
        error = abs(observed-reference)
        max_probability_error = max(max_probability_error, error)
        assert error < .006
    for fixture in range(100):
        n = 3 if fixture % 2 else 7
        probabilities = rng.random(n)
        h = int(rng.integers(1, n+1))
        scalar = 0.
        for votes in itertools.product([0, 1], repeat=n):
            if sum(votes) >= h:
                scalar += float(np.prod([probabilities[i] if v else 1-probabilities[i] for i, v in enumerate(votes)]))
        actual = float(tail(probabilities, h))
        max_tail_error = max(max_tail_error, abs(actual-scalar))
        assert abs(actual-scalar) < 1e-12
    return dict(CDF_exact_fixtures=7, continuous_jitter_Monte_Carlo_fixtures=20,
                draws_per_probability_fixture=200000, max_probability_Monte_Carlo_error=max_probability_error,
                explicit_vote_enumerations=100, maximum_tail_error=max_tail_error,
                ideal_continuous_jitter_law=True, machine_rounding_not_simulated_by_closed_form=True)


def main():
    output = R / 'V197_TIE_POLICY_AUDIT.json'
    assert not output.exists()
    fixtures = technical()
    rows, retention, sources = [], [], {}
    max_old_parity_error = 0.
    for k in [4, 8, 12]:
        losses = population(k)
        for rule in ['UNANIMITY', 'MAJORITY']:
            h = k-1 if rule == 'UNANIMITY' else k//2
            parent_npz = R/f'V195_CORRELATED_EXPLORATION/V195_k{k}_{rule}_W32_G20_T8000.npz'
            parent_json = parent_npz.with_suffix('.json')
            parent_raw = json.loads(parent_json.read_text(encoding='utf-8'))
            parent_audit = json.loads((parent_npz.parent/f'V195A_FROZEN_NO_PULSE_AUDIT_k{k}_{rule}.json').read_text(encoding='utf-8'))
            data = np.load(parent_npz)
            new_initial, old_initial = None, None
            for path in [parent_npz, parent_json]:
                sources[path.relative_to(B).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            assert parent_raw['source_sha256'] == hashlib.sha256((B/'v195_joint_signal_policy_exploration.py').read_bytes()).hexdigest()
            for arm in data.files:
                q = data[arm]
                new, _, _ = evaluate(q, losses, h, arm, True)
                old, _, _ = evaluate(q, losses, h, arm, False)
                ref = next(r for r in parent_audit['rows'] if r['arm'] == arm)['exact_welfare']
                error = abs(float(old.mean())-ref)
                max_old_parity_error = max(max_old_parity_error, error)
                assert error < 1e-12
                discrepancy = np.abs(yes_probability(q)-yes_probability(q, False))
                observed = next(r for r in parent_raw['rows'] if r['arm'] == arm)['phases'][-1]['world_reward_mean']
                rows.append(dict(study='V195_voting', k=k, rule=rule, arm=arm,
                    old_expected_welfare=float(old.mean()), corrected_expected_welfare=float(new.mean()),
                    correction=float((new-old).mean()), observed_frozen_deployment_welfare=observed,
                    max_action_probability_discrepancy=float(discrepancy.max()),
                    states_with_probability_discrepancy=int((discrepancy > 1e-12).sum()),
                    corrected_world_welfare=new.tolist()))
                if arm == 'JOINT_SIGNAL_PULSE_10':
                    new_initial, old_initial = new, old
            final_npz = R/f'V196_POST_PULSE_PLASTICITY/V196_k{k}_{rule}_W32_G20_H8000.npz'
            final_json = final_npz.with_suffix('.json')
            raw = json.loads(final_json.read_text(encoding='utf-8'))
            final_data = np.load(final_npz)
            assert raw['method_sha'] == hashlib.sha256((B/'v196_plastic_no_pulse_maintenance.py').read_bytes()).hexdigest()
            for path in [final_npz, final_json]:
                sources[path.relative_to(B).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            corrected_ends = {}
            for arm in final_data.files:
                q = final_data[arm]
                if arm == 'FREEZE':
                    assert np.array_equal(q, data['JOINT_SIGNAL_PULSE_10'])
                new, _, _ = evaluate(q, losses, h, arm, True)
                old, _, _ = evaluate(q, losses, h, arm, False)
                old_record = next(r for r in raw['results'] if r['arm'] == arm)
                error = abs(float(old.mean())-old_record['checkpoints'][-1]['mean_welfare'])
                max_old_parity_error = max(max_old_parity_error, error)
                assert error < 1e-12
                discrepancy = np.abs(yes_probability(q)-yes_probability(q, False))
                corrected_ends[arm] = new
                rows.append(dict(study='V196_voting', k=k, rule=rule, arm=arm,
                    old_expected_welfare=float(old.mean()), corrected_expected_welfare=float(new.mean()),
                    correction=float((new-old).mean()),
                    old_retention_ratio=float(old.mean()/old_initial.mean()),
                    corrected_retention_ratio=float(new.mean()/new_initial.mean()),
                    max_action_probability_discrepancy=float(discrepancy.max()),
                    states_with_probability_discrepancy=int((discrepancy > 1e-12).sum()),
                    corrected_world_welfare=new.tolist()))
            end = corrected_ends['PLASTIC_NO_PULSE_EPS08']
            keep = corrected_ends['PLASTIC_KEEP_PULSE_10']
            rng = np.random.default_rng(197000+k+(rule == 'MAJORITY'))
            indices = rng.integers(0, W, size=(10000, W))
            benefit = keep-end
            ci = np.quantile(benefit[indices].mean(1), [.025, .975]).tolist()
            retention.append(dict(k=k, rule=rule, corrected_initial=float(new_initial.mean()),
                corrected_no_pulse_end=float(end.mean()), corrected_keep_pulse_end=float(keep.mean()),
                corrected_retention_ratio=float(end.mean()/new_initial.mean()),
                meets75percent=bool(end.mean()/new_initial.mean() >= .75),
                corrected_pulse_maintenance_benefit=float(benefit.mean()), paired_world_CI95=ci))
    primary_count = sum(r['meets75percent'] for r in retention)
    result = dict(new_training_executed=False, previous_sources_and_Q_arrays_preserved=True,
        issue='Uniform-jitter tie selection induces triangular probabilities within the tolerance interval, not constant .5.',
        formula='z=(Q_yes-Q_no)/1e-12; p_yes=(1+z)^2/2 for -1<z<0, 1-(1-z)^2/2 for 0<=z<1; 0/1 outside.',
        technical=fixtures, source_sha256=sources, policy_arrays=len(rows),
        maximum_reproduction_error_for_previous_evaluator=max_old_parity_error,
        maximum_absolute_welfare_correction=max(abs(r['correction']) for r in rows),
        primary_retention_conditions_meeting75percent=primary_count,
        previous_primary_maintenance_failure_survives_correction=bool(primary_count < 4),
        all_corrected_pulse_benefit_CIs_positive=all(r['paired_world_CI95'][0] > 0 for r in retention),
        intermediate_V196_Q_checkpoints_not_saved_and_not_recomputed=True,
        endpoint_values_corrected_only=True, rows=rows, retention=retention,
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['rows', 'source_sha256']}, indent=2), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
