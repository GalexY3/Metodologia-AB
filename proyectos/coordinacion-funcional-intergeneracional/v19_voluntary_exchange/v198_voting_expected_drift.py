"""Conditional-mean private-Q drift after removal of coordinated pulses.

This is an oracle diagnostic, not an implementable decentralized learner.
Iterating conditional means is NOT the mean of nonlinear stochastic trajectories.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import time
import numpy as np
from numba import njit, prange
from research_resource_limits import apply_limits
from v197_tie_policy_audit import yes_probability, population, evaluate

B = Path(__file__).resolve().parent
R = B / 'results'
OUT = R / 'V198_VOTING_EXPECTED_DRIFT'
H = 8000


@njit(cache=True)
def leave_one_out(full, probability):
    """Stable polynomial division, choosing the non-amplifying direction."""
    n = len(full)-1
    other = np.zeros(n)
    if probability <= .5:
        other[0] = full[0]/(1-probability)
        for j in range(1, n):
            other[j] = (full[j]-probability*other[j-1])/(1-probability)
    else:
        other[n-1] = full[n]/probability
        for j in range(n-2, -1, -1):
            other[j] = (full[j+1]-(1-probability)*other[j+1])/probability
    for j in range(n):
        assert other[j] >= -1e-12
        other[j] = max(0., other[j])
    assert abs(other.sum()-1) < 2e-11
    return other


@njit(cache=True, parallel=True)
def targets_and_visitation(yes, losses, threshold):
    groups, n = losses.shape
    targets = np.zeros((groups, n, 2, 2))
    visit = np.zeros_like(targets)
    for group in prange(groups):
        probs = np.empty((2, n))
        full = np.zeros((2, n+1))
        for state in range(2):
            full[state, 0] = 1.
            for i in range(n):
                prob = (.8*yes[group, i, 1]+.2*yes[group, i, 0] if state == 0
                        else .2*yes[group, i, 1]+.8*yes[group, i, 0])
                probs[state, i] = prob
                for count in range(i+1, 0, -1):
                    full[state, count] = full[state, count]*(1-prob)+full[state, count-1]*prob
                full[state, 0] *= 1-prob
        for i in range(n):
            other_good = leave_one_out(full[0], probs[0, i])
            other_bad = leave_one_out(full[1], probs[1, i])
            tail_good = other_good[threshold:].sum()
            tail_bad = other_bad[threshold:].sum()
            pivotal_good = other_good[threshold-1]
            pivotal_bad = other_bad[threshold-1]
            for signal in range(2):
                likelihood_good = .8 if signal else .2
                likelihood_bad = 1-likelihood_good
                prob_signal = .6*likelihood_good+.4*likelihood_bad
                for action in range(2):
                    approval_good = tail_good+action*pivotal_good
                    approval_bad = tail_bad+action*pivotal_bad
                    expected_reward = .6*likelihood_good*approval_good-.4*likelihood_bad*losses[group, i]*approval_bad
                    targets[group, i, signal, action] = expected_reward/prob_signal
                    choice = yes[group, i, signal] if action else 1-yes[group, i, signal]
                    visit[group, i, signal, action] = prob_signal*choice
    return targets, visit


def technical():
    output = R / 'V198_EXPECTED_DRIFT_TECHNICAL.json'
    assert not output.exists() and not OUT.exists()
    rng = np.random.default_rng(198553)
    max_error, entries = 0., 0
    for fixture in range(50):
        n = 3 if fixture % 2 else 7
        h = n if fixture % 3 else n//2+1
        q = rng.normal(size=(1, n, 2, 2))
        losses = np.where(rng.random((1, n)) < .5, 1., 7.)
        eps = .08 if fixture % 2 else 0.
        yes = eps/2+(1-eps)*yes_probability(q)
        targets, visit = targets_and_visitation(yes, losses, h)
        for i in range(n):
            others = [j for j in range(n) if j != i]
            for signal in range(2):
                lg = .8 if signal else .2
                lb = 1-lg
                prob_signal = .6*lg+.4*lb
                for action in range(2):
                    expected = 0.
                    for good, prior, likelihood in [(True, .6, lg), (False, .4, lb)]:
                        for votes in itertools.product([0, 1], repeat=n-1):
                            prob_votes = 1.
                            for j, vote in zip(others, votes):
                                probability = ((.8 if good else .2)*yes[0, j, 1]+
                                               (.2 if good else .8)*yes[0, j, 0])
                                prob_votes *= probability if vote else 1-probability
                            reward = (1. if good else -losses[0, i]) if sum(votes)+action >= h else 0.
                            expected += prior*likelihood*prob_votes*reward/prob_signal
                    error = abs(targets[0, i, signal, action]-expected)
                    max_error = max(max_error, error)
                    assert error < 2e-11
                    own_prob = yes[0, i, signal] if action else 1-yes[0, i, signal]
                    assert abs(visit[0, i, signal, action]-prob_signal*own_prob) < 1e-14
                    entries += 1
    result = dict(synthetic_fixtures=50, conditional_payoff_entries_enumerated=entries,
                  maximum_error=max_error, original_parent_states_not_used_for_dynamics=True,
                  no_scientific_trajectory_executed=True, leave_one_out_probabilities_validated=True)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('V198_TECHNICAL', json.dumps(result), flush=True)


def one_case(k, rule, epsilon):
    parent = R/f'V195_CORRELATED_EXPLORATION/V195_k{k}_{rule}_W32_G20_T8000.npz'
    original = np.load(parent)['JOINT_SIGNAL_PULSE_10']
    q = original.copy().reshape(32*20, k-1, 2, 2)
    losses_full = population(k)
    losses = losses_full.reshape(32*20, k-1)
    h = k-1 if rule == 'UNANIMITY' else k//2
    arm = 'MEAN_EPS08' if epsilon else 'MEAN_EPS00'
    name = f'k{k}_{rule}_{arm}'
    history = []
    started = time.monotonic()
    for step in range(H+1):
        if step % 2000 == 0:
            shaped = q.reshape(original.shape)
            world, good, bad = evaluate(shaped, losses_full, h, arm, True)
            history.append(dict(step=step, mean_welfare=float(world.mean()), world_welfare=world.tolist(),
                                mean_good_approval=float(good.mean()), mean_bad_approval=float(bad.mean())))
            np.savez_compressed(OUT/f'{name}_step{step}.npz', Q=shaped)
            print('V198', name, step, 'value', round(float(world.mean()), 6),
                  'seconds', round(time.monotonic()-started, 1), flush=True)
        if step == H:
            break
        yes = epsilon/2+(1-epsilon)*yes_probability(q)
        targets, visitation = targets_and_visitation(yes, losses, h)
        # Mean of one realized private-Q increment, evaluated at current Q.
        q += .10*visitation*(targets-q)
        assert np.isfinite(q).all()
    ratio = history[-1]['mean_welfare']/history[0]['mean_welfare']
    result = dict(k=k, rule=rule, arm=arm, epsilon=epsilon, alpha=.10, steps=H,
                  parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),
                  history=history, final_retention_ratio=float(ratio), meets75percent=bool(ratio >= .75),
                  expected_increment_not_expected_nonlinear_trajectory=True,
                  oracle_diagnostic_not_a_decentralized_private_learner=True)
    (OUT/f'{name}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def run():
    receipt = json.loads((R/'V198_EXPECTED_DRIFT_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path, sha in dict(receipt['source_sha256'], **receipt['binary_parent_sha256']).items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    OUT.mkdir(exist_ok=False)
    (OUT/'MANIFEST.json').write_text(json.dumps(dict(preregistration=receipt,
        mean_dynamics_oracle_diagnostic=True, independent_new_roots=0), indent=2), encoding='utf-8')
    results = [one_case(k, rule, eps) for k in [4, 8, 12]
               for rule in ['UNANIMITY', 'MAJORITY'] for eps in [.08, 0.]]
    counts = {arm: sum(r['meets75percent'] for r in results if r['arm'] == arm)
              for arm in ['MEAN_EPS08', 'MEAN_EPS00']}
    summary = dict(results=results, retention75_counts=counts,
        MEAN_EPS08_retains_in_at_least_four=bool(counts['MEAN_EPS08'] >= 4),
        sampling_noise_alone_refuted_in_at_least_four=bool(counts['MEAN_EPS08'] <= 2),
        oracle_diagnostic_not_a_proposed_institution=True, independent_new_roots=0,
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('V198_COMPLETE', json.dumps({k: v for k, v in summary.items() if k != 'results'}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['technical', 'run'])
    a = p.parse_args()
    print('LIMITS', apply_limits(2), flush=True)
    {'technical': technical, 'run': run}[a.command]()
