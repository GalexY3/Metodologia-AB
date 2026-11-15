"""Published private learners: formation, maintenance and signal reversal.

No agent sees truth, other signals, other Qs or counterfactual rewards. Methods
are assigned by the experimenter; the voting institution is not invented here.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import math
import time
import numpy as np
from numba import njit, prange
from research_resource_limits import apply_limits
from v197_tie_policy_audit import population, yes_probability, tail

B = Path(__file__).resolve().parent
R = B/'results'
OUT = R/'V199_PRIVATE_BASELINES'
W, G, PRE, END, CHUNK = 32, 20, 8000, 12000, 100
NAMES = ['IQL_JITTER', 'IQL_EXACT', 'IQL_SLOW', 'HYSTERETIC', 'RUNNING_MEAN', 'LMRL2', 'FROZEN', 'IQL_MIN']


def json_default(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, default=json_default), encoding='utf-8')


@njit(cache=True)
def choose_private(q0, q1, t0, t1, method, epsilon, coins):
    if method == 0:
        greedy = int(q1+1e-12*coins[1] > q0+1e-12*coins[0])
    else:
        greedy = 1 if q1 > q0 else (0 if q0 > q1 else int(coins[0] < .5))
    if method == 5:
        average_temp = .5*(t0+t1)
        if average_temp >= 2.:
            logit = max(-700., min(700., (q1-q0)/average_temp))
            return int(coins[2] < 1./(1.+math.exp(-logit)))
        return greedy
    if method == 6:
        return greedy
    return int(2*coins[3]) if coins[2] < epsilon else greedy


@njit(cache=True)
def learn_private(old, reward, count, temperature, method, coin):
    if method == 6:
        return old, count, temperature
    count += 1
    delta = reward-old
    if method == 2:
        rate = .01
    elif method == 3:
        rate = .1 if delta >= 0 else .01
    elif method == 4:
        rate = 1./(9+count)
    else:
        rate = .1
    if method == 5:
        accept = delta >= 0 or coin < -math.expm1(-1./temperature)
        return old+(rate*delta if accept else 0.), count, .995*temperature
    return old+rate*delta, count, temperature


@njit(cache=True, parallel=True)
def update_chunk(q, counts, temperatures, losses, method_ids, environment, coins, epsilons, accuracies, quorum):
    methods, worlds, groups, agents = q.shape[:4]
    observed = np.zeros((methods, worlds, groups, 4))
    for flat in prange(worlds*groups):
        w, g = flat//groups, flat % groups
        signals = np.empty(agents, dtype=np.int64)
        actions = np.empty(agents, dtype=np.int64)
        for t in range(len(environment)):
            good = environment[t, w, g, 0] < .6
            probability_positive = accuracies[t] if good else 1-accuracies[t]
            for i in range(agents):
                signals[i] = int(environment[t, w, g, i+1] < probability_positive)
            for method_index in range(methods):
                method = method_ids[method_index]
                yes = 0
                for i in range(agents):
                    s = signals[i]
                    actions[i] = choose_private(q[method_index, w, g, i, s, 0], q[method_index, w, g, i, s, 1],
                        temperatures[method_index, w, g, i, s, 0], temperatures[method_index, w, g, i, s, 1],
                        method, epsilons[t], coins[t, w, g, i])
                    yes += actions[i]
                accepted = yes >= quorum
                observed[method_index, w, g, 3] += int(accepted)
                for i in range(agents):
                    reward = (1. if good else -losses[w, g, i]) if accepted else 0.
                    observed[method_index, w, g, 0] += reward/agents
                    observed[method_index, w, g, 1 if losses[w, g, i] == 1 else 2] += reward
                    s, a = signals[i], actions[i]
                    value, count, temperature = learn_private(q[method_index, w, g, i, s, a], reward,
                        counts[method_index, w, g, i, s, a], temperatures[method_index, w, g, i, s, a],
                        method, coins[t, w, g, i, 4])
                    q[method_index, w, g, i, s, a] = value
                    counts[method_index, w, g, i, s, a] = count
                    temperatures[method_index, w, g, i, s, a] = temperature
    return observed


def policy_probabilities(q, temperatures, method_ids, epsilon, native):
    delta = q[..., 1]-q[..., 0]
    yes = np.where(delta > 0, 1., np.where(delta < 0, 0., .5))
    for j, method in enumerate(method_ids):
        if method == 0:
            yes[j] = yes_probability(q[j])
        if native and method == 5:
            mean_temperature = temperatures[j].mean(-1)
            logit = np.clip(delta[j]/np.maximum(mean_temperature, 1e-300), -700, 700)
            yes[j] = np.where(mean_temperature >= 2, 1/(1+np.exp(-logit)), yes[j])
        elif native and method != 6:
            yes[j] = epsilon/2+(1-epsilon)*yes[j]
    return yes


def evaluate(q, temperatures, losses, method_ids, epsilon, accuracy, quorum):
    rows = []
    low = losses == 1
    high = ~low
    assert np.all(low.sum((1, 2)) > 0) and np.all(high.sum((1, 2)) > 0)
    for native in [False, True]:
        yes = policy_probabilities(q, temperatures, method_ids, epsilon, native)
        approve_good = tail(accuracy*yes[..., 1]+(1-accuracy)*yes[..., 0], quorum)
        approve_bad = tail((1-accuracy)*yes[..., 1]+accuracy*yes[..., 0], quorum)
        payoffs = .6*approve_good[..., None]-.4*losses[None]*approve_bad[..., None]
        world = payoffs.mean((2, 3))
        world_low = (payoffs*low[None]).sum((2, 3))/low.sum((1, 2))[None]
        world_high = (payoffs*high[None]).sum((2, 3))/high.sum((1, 2))[None]
        for j, method in enumerate(method_ids):
            if not native:
                rows.append(dict(method=NAMES[method], greedy_world_welfare=world[j].tolist(),
                    greedy_mean_welfare=float(world[j].mean()), greedy_world_low_payoff=world_low[j].tolist(),
                    greedy_world_high_payoff=world_high[j].tolist(), greedy_low_payoff=float(world_low[j].mean()),
                    greedy_high_payoff=float(world_high[j].mean()), greedy_good_approval=float(approve_good[j].mean()),
                    greedy_bad_approval=float(approve_bad[j].mean())))
            else:
                rows[j].update(native_mean_welfare=float(world[j].mean()), native_world_welfare=world[j].tolist(),
                    native_low_payoff=float(world_low[j].mean()), native_high_payoff=float(world_high[j].mean()))
    return rows


def rng_for(cohort, k, rule, w, stream):
    entropy = [199, 0 if cohort == 'MAINTENANCE' else 1, k, 0 if rule == 'UNANIMITY' else 1, w, stream]
    return np.random.Generator(np.random.Philox(np.random.SeedSequence(entropy)))


def epsilon_at(step, cohort):
    return .3-.22*min(step, 6000)/6000 if cohort == 'FORMATION' and step < PRE else .08


def checkpoint(folder, step, q, counts, temperatures, env_rngs, action_rngs):
    states = json.dumps(dict(environment=[r.bit_generator.state for r in env_rngs],
                             actions=[r.bit_generator.state for r in action_rngs]), default=json_default)
    np.savez_compressed(folder/f'checkpoint_{step}.npz', Q=q, counts=counts, temperatures=temperatures,
                        step=np.array(step), rng_json=np.array(states))


def one_case(cohort, k, rule):
    folder = OUT/f'{cohort}_k{k}_{rule}'
    folder.mkdir(exist_ok=False)
    ids = np.array([0, 1, 2, 3, 4, 5, 6 if cohort == 'MAINTENANCE' else 7], dtype=np.int64)
    n, h = k-1, k-1 if rule == 'UNANIMITY' else k//2
    if cohort == 'MAINTENANCE':
        losses = population(k)
        path = R/f'V195_CORRELATED_EXPLORATION/V195_k{k}_{rule}_W32_G20_T8000.npz'
        parent = np.load(path)['JOINT_SIGNAL_PULSE_10']
        q = np.repeat(parent[None], len(ids), axis=0)
    else:
        losses = np.stack([np.where(rng_for(cohort, k, rule, w, 0).random((G, n)) < .5, 1., 7.) for w in range(W)])
        q = np.zeros((len(ids), W, G, n, 2, 2))
        for j, method in enumerate(ids):
            if method in [5, 7]:
                q[j] = -losses[..., None, None]
        parent = None
    assert q.dtype == np.float64
    counts = np.zeros(q.shape, dtype=np.int64)
    temperatures = np.full(q.shape, 50.)
    env_rngs = [rng_for(cohort, k, rule, w, 1) for w in range(W)]
    action_rngs = [rng_for(cohort, k, rule, w, 2) for w in range(W)]
    np.savez_compressed(folder/'CONTEXT.npz', losses=losses, method_ids=ids)
    histories = [[] for _ in ids]
    accum = np.zeros((2, len(ids), W, G, 4))
    start = time.monotonic()

    def record(step):
        accuracy = .8 if step <= PRE else .2
        rows = evaluate(q, temperatures, losses, ids, epsilon_at(step, cohort), accuracy, h)
        for j, row in enumerate(rows):
            row.update(step=step, accuracy=accuracy)
            histories[j].append(row)
        if step % 4000 == 0:
            checkpoint(folder, step, q, counts, temperatures, env_rngs, action_rngs)
        if step == PRE:
            dump(folder/'INVERSION_WITHOUT_LEARNING.json', evaluate(q, temperatures, losses, ids, .08, .2, h))
        print('V199', cohort, k, rule, step,
              {row['method']: round(row['greedy_mean_welfare'], 5) for row in rows},
              'seconds', round(time.monotonic()-start, 1), flush=True)

    record(0)
    for begin in range(0, END, CHUNK):
        environment = np.empty((CHUNK, W, G, n+1))
        coins = np.empty((CHUNK, W, G, n, 5))
        for w in range(W):
            environment[:, w] = env_rngs[w].random((CHUNK, G, n+1))
            coins[:, w] = action_rngs[w].random((CHUNK, G, n, 5))
        epsilons = np.array([epsilon_at(step, cohort) for step in range(begin, begin+CHUNK)])
        accuracies = np.array([.8 if step < PRE else .2 for step in range(begin, begin+CHUNK)])
        phase = int(begin >= PRE)
        accum[phase] += update_chunk(q, counts, temperatures, losses, ids, environment, coins, epsilons, accuracies, h)
        if (begin+CHUNK) % 1000 == 0:
            record(begin+CHUNK)
        if parent is not None:
            assert np.array_equal(q[-1], parent)
    results = []
    for j, method in enumerate(ids):
        initial, before, final = histories[j][0], histories[j][PRE//1000], histories[j][-1]
        retention = before['greedy_mean_welfare']/initial['greedy_mean_welfare'] if cohort == 'MAINTENANCE' else None
        recovery = final['greedy_mean_welfare']/before['greedy_mean_welfare'] if before['greedy_mean_welfare'] > .01 else None
        observed = []
        for phase, steps in [(0, PRE), (1, END-PRE)]:
            observed.append(dict(phase='BEFORE_REVERSAL' if phase == 0 else 'AFTER_REVERSAL',
                world_welfare=(accum[phase, j, :, :, 0].mean(1)/steps).tolist(),
                mean_welfare=float(accum[phase, j, :, :, 0].mean()/steps),
                mean_low_payoff=float(np.mean(accum[phase, j, :, :, 1].sum(1)/(losses == 1).sum((1, 2))/steps)),
                mean_high_payoff=float(np.mean(accum[phase, j, :, :, 2].sum(1)/(losses == 7).sum((1, 2))/steps)),
                mean_approval=float(accum[phase, j, :, :, 3].mean()/steps)))
        result = dict(cohort=cohort, k=k, rule=rule, method=NAMES[method], history=histories[j],
            retention_ratio=retention, reversal_recovery_ratio=recovery,
            maintenance_passed=bool(retention is not None and retention >= .75 and before['greedy_low_payoff'] >= 0 and before['greedy_high_payoff'] >= 0),
            adaptation_passed=bool(before['greedy_mean_welfare'] >= .05 and recovery is not None and recovery >= .75
                                   and final['greedy_low_payoff'] >= 0 and final['greedy_high_payoff'] >= 0),
            observed_private_payoffs=observed, pulse_rate=0., shared_parameters=False,
            institution_or_method_choice_learned=False)
        dump(folder/f'{NAMES[method]}.json', result)
        results.append(result)
    dump(folder/'SUMMARY.json', dict(runs=results, new_world_roots=32 if cohort == 'FORMATION' else 0,
        independent_worlds_are_the_inference_unit=True, parent_history_reused=cohort == 'MAINTENANCE'))
    return results


def technical():
    output = R/'V199_PRIVATE_BASELINES_TECHNICAL.json'
    assert not output.exists() and not OUT.exists()
    rng = np.random.default_rng(199553)
    action_checks = update_checks = 0
    max_error = 0.
    for method in range(8):
        for _ in range(100):
            q0, q1 = rng.normal(size=2)
            t0, t1 = rng.uniform(.01, 50, size=2)
            coins = rng.random(5)
            if method == 0:
                greedy = int(q1+1e-12*coins[1] > q0+1e-12*coins[0])
            else:
                greedy = int(q1 > q0) if q0 != q1 else int(coins[0] < .5)
            if method == 5 and (t0+t1)/2 >= 2:
                expected = int(coins[2] < 1/(1+np.exp(-(q1-q0)/((t0+t1)/2))))
            elif method in [5, 6]:
                expected = greedy
            else:
                expected = int(2*coins[3]) if coins[2] < .08 else greedy
            assert choose_private(q0, q1, t0, t1, method, .08, coins) == expected
            action_checks += 1
            old, reward = rng.normal(size=2)
            count = int(rng.integers(100))
            temp, coin = float(rng.uniform(.01, 50)), float(rng.random())
            next_count = count if method == 6 else count+1
            delta = reward-old
            rate = .01 if method == 2 or (method == 3 and delta < 0) else (1/(9+next_count) if method == 4 else .1)
            accept = method != 6 and (method != 5 or delta >= 0 or coin < 1-np.exp(-1/temp))
            expected_value = old+rate*delta if accept else old
            expected_temp = .995*temp if method == 5 else temp
            actual = learn_private(old, reward, count, temp, method, coin)
            error = max(abs(actual[0]-expected_value), abs(actual[2]-expected_temp))
            max_error = max(max_error, error)
            assert error < 1e-12 and actual[1] == next_count
            update_checks += 1
    # Different group batching must leave every local history identical.
    methods = np.arange(8, dtype=np.int64)
    q = rng.normal(size=(8, 2, 3, 3, 2, 2)); counts = np.zeros(q.shape, dtype=np.int64); temp = np.full(q.shape, 50.)
    losses = np.where(rng.random((2, 3, 3)) < .5, 1., 7.)
    env, coins = rng.random((20, 2, 3, 4)), rng.random((20, 2, 3, 3, 5))
    original = q.copy()
    eps, acc = np.full(20, .08), np.full(20, .8)
    observed = update_chunk(q, counts, temp, losses, methods, env, coins, eps, acc, 2)
    for w in range(2):
        for g in range(3):
            small = original[:, w:w+1, g:g+1].copy()
            c, t = np.zeros(small.shape, dtype=np.int64), np.full(small.shape, 50.)
            values = update_chunk(small, c, t, losses[w:w+1, g:g+1], methods,
                                 env[:, w:w+1, g:g+1].copy(), coins[:, w:w+1, g:g+1].copy(), eps, acc, 2)
            assert np.array_equal(small, q[:, w:w+1, g:g+1])
            assert np.array_equal(c, counts[:, w:w+1, g:g+1])
            assert np.array_equal(t, temp[:, w:w+1, g:g+1])
            assert np.array_equal(values, observed[:, w:w+1, g:g+1])
    assert np.array_equal(q[6], original[6])
    # Exercise the real world kernel with known frozen votes, then compare
    # its accumulated returns with explicit scalar physical accounting.
    reward_checks = 0
    for _ in range(30):
        n = int(rng.choice([3, 7, 11])); h = n if rng.random() < .5 else n//2+1
        votes = rng.integers(2, size=n); truths = rng.integers(2, size=20)
        loss = np.where(rng.random(n) < .5, 1., 7.)
        frozen = np.empty((1, 1, 1, n, 2, 2))
        for i, a in enumerate(votes):
            frozen[0, 0, 0, i, :, a] = 2.; frozen[0, 0, 0, i, :, 1-a] = -2.
        before = frozen.copy()
        environmental = rng.random((20, 1, 1, n+1))
        environmental[:, 0, 0, 0] = np.where(truths, .1, .9)
        values = update_chunk(frozen, np.zeros(frozen.shape, dtype=np.int64), np.full(frozen.shape, 50.),
            loss[None, None], np.array([6], dtype=np.int64), environmental,
            rng.random((20, 1, 1, n, 5)), np.full(20, .08), np.full(20, .8), h)
        scalar = np.zeros(4)
        accepted = sum(int(v) for v in votes) >= h
        for good in truths:
            for i, l in enumerate(loss):
                reward = (1. if good else -l) if accepted else 0.
                scalar[0] += reward/n
                scalar[1 if l == 1 else 2] += reward
                reward_checks += 1
            scalar[3] += int(accepted)
        assert np.max(np.abs(values[0, 0, 0]-scalar)) < 1e-11
        assert np.array_equal(frozen, before)
    # Known actions exercise selected-state writes in the complete kernel.
    for good in [False, True]:
        fixture = np.zeros((8, 1, 1, 3, 2, 2)); fixture[..., 0] = -100.
        loss = np.array([[[1., 7., 1.]]])
        cc, tt = np.zeros(fixture.shape, dtype=np.int64), np.full(fixture.shape, 50.)
        environmental = np.full((1, 1, 1, 4), .1); environmental[0, 0, 0, 0] = .1 if good else .9
        coins = np.zeros((1, 1, 1, 3, 5)); coins[..., 3] = .9
        update_chunk(fixture, cc, tt, loss, methods, environmental, coins, np.array([.08]), np.array([.8]), 3)
        for j, method in enumerate(methods):
            for i, l in enumerate(loss[0, 0]):
                reward = 1. if good else -l
                rate = .01 if method == 2 or (method == 3 and not good) else .1
                expected = 0. if method == 6 else rate*reward
                assert abs(fixture[j, 0, 0, i, 1, 1]-expected) < 1e-12
                assert fixture[j, 0, 0, i, 0, 1] == 0 and fixture[j, 0, 0, i, 1, 0] == -100.
    # Check near-tie and native-temperature probabilities against actual actions.
    fixture = np.zeros((8, 1, 1, 1, 2, 2)); fixture[..., 1] = .5e-12
    probabilities = policy_probabilities(fixture, np.full(fixture.shape, 50.), methods, .08, True)[:, 0, 0, 0, 0]
    max_probability_error = 0.
    for j, method in enumerate(methods):
        coins = rng.random((50000, 5))
        frequency = np.mean([choose_private(0., .5e-12, 50., 50., method, .08, coin) for coin in coins])
        error = abs(frequency-probabilities[j]); max_probability_error = max(max_probability_error, error)
        assert error < .012
    test_rng = rng_for('FORMATION', 4, 'UNANIMITY', 0, 1)
    state = json.loads(json.dumps(test_rng.bit_generator.state, default=json_default))
    restored = np.random.Generator(np.random.Philox(0)); restored.bit_generator.state = state
    assert np.array_equal(test_rng.random(1000), restored.random(1000))
    result = dict(private_action_fixture_checks=action_checks, private_update_fixture_checks=update_checks,
        maximum_update_error=max_error, scalar_reward_entries=reward_checks, independent_group_isolation_checks=6,
        full_kernel_selected_state_write_checks=48, native_choice_probability_checks=8,
        maximum_choice_Monte_Carlo_error=float(max_probability_error),
        all_isolated_histories_and_observed_rewards_bit_identical=True, frozen_Q_unchanged=True,
        RNG_JSON_roundtrip_bit_identical=True, real_parent_states_not_used_for_training=True, scientific_training_executed=False)
    dump(output, result); print('V199_TECHNICAL', json.dumps(result), flush=True)


def run():
    receipt = json.loads((R/'V199_PRIVATE_BASELINES_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path, sha in dict(receipt['source_sha256'], **receipt['binary_parent_sha256']).items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    OUT.mkdir(exist_ok=False)
    dump(OUT/'MANIFEST.json', dict(preregistration=receipt, started_UTC=datetime.now(timezone.utc).isoformat(),
        new_formation_world_roots=192, group_membership_rule_and_learning_methods_imposed=True,
        private_reward_only=True, coordinated_pulses_used=False, NumPy=np.__version__, GPU_used=False))
    results = [run for cohort in ['MAINTENANCE', 'FORMATION'] for k in [4, 8, 12]
               for rule in ['UNANIMITY', 'MAJORITY'] for run in one_case(cohort, k, rule)]
    summary = dict(runs=[{k: v for k, v in r.items() if k != 'history'} for r in results],
        maintenance_counts={m: sum(r['maintenance_passed'] for r in results if r['cohort'] == 'MAINTENANCE' and r['method'] == m)
                            for m in NAMES if m != 'IQL_MIN'},
        adaptation_counts={cohort: {m: sum(r['adaptation_passed'] for r in results if r['cohort'] == cohort and r['method'] == m)
                                   for m in NAMES if any(r['cohort'] == cohort and r['method'] == m for r in results)}
                           for cohort in ['MAINTENANCE', 'FORMATION']},
        formation_new_independent_world_roots=192, methods_paired_within_each_world=True,
        original_maintenance_parents_reused=True, original_scientific_contribution_accredited=False,
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    dump(OUT/'SUMMARY.json', summary)
    print('V199_COMPLETE', json.dumps({k: v for k, v in summary.items() if k != 'runs'}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('command', choices=['technical', 'run']); a = p.parse_args()
    print('LIMITS', apply_limits(2), flush=True)
    {'technical': technical, 'run': run}[a.command]()
