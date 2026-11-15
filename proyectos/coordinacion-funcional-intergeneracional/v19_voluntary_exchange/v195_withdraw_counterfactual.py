"""Withdraw counterfactual feedback at training-selected memorization.

This neural experiment has a distinct namespace from the pre-existing V195
private-voting experiments. All parent histories and AdamW moments are retained.
Only scalar realized payoffs enter either learner after its own intervention cut.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
from pathlib import Path
import argparse
import copy
import hashlib
import json
import time
from datetime import datetime, timezone
import numpy as np
import torch
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver
from v191_dual_neural_credit import (P, N, EPS, SEEDS, sample_action,
                                     sampling_probability, bandit_loss)
from v192_dual_neural_learning import evaluate
from v193_frozen_peer import (data_for, initial, load_group, export_one,
                              compare_tensors)

BASE = Path(__file__).resolve().parent
OUT = BASE / 'results/V195_WITHDRAW_COUNTERFACTUAL'
END = 60000
ARMS = [('BOTH_BANDIT', None), ('FREEZE_A_BANDIT_B', 0), ('FREEZE_B_BANDIT_A', 1)]


def realized_rewards(fa, fb, action_a, action_b, permutation, p=P):
    """World calculation only; no counterfactual table is constructed."""
    target = (fa + fb.gather(1, permutation)) % p
    ra = (((action_a + action_b.gather(1, permutation)) % p) == target).float()
    return ra, torch.zeros_like(ra).scatter(1, permutation, ra)


def update(models, optimizers, rngs, tensors, active):
    coins = torch.tensor(np.stack([r.random((2, N)) for r in rngs]), device='cuda')
    permutation = torch.tensor(np.stack([r.permutation(N) for r in rngs]), device='cuda')
    a, b, f = [tensors[k] for k in ['a', 'b', 'f']]
    values = [models[r](a[:, r], b[:, r]) for r in range(2)]
    greedy = [v.detach().argmax(2) for v in values]
    actions = [sample_action(greedy[r], coins[:, r]) for r in range(2)]
    rewards = realized_rewards(f[:, 0], f[:, 1], actions[0], actions[1], permutation)
    # These loss calls have no access to f, partner policy, or unchosen rewards.
    losses = [bandit_loss(values[r], actions[r], rewards[r],
                         sampling_probability(actions[r], greedy[r]))
              if active[r] else None for r in range(2)]
    for r in range(2):
        if active[r]:
            optimizers[r].zero_grad(set_to_none=True)
            losses[r].backward()
            optimizers[r].step()


def parent_spec():
    parents = [initial(seed) for seed in SEEDS]
    cuts = [p['step'] for p in parents]
    gauges = [p['history'][-1]['train_chosen_gauge_A'] for p in parents]
    assert cuts == [1200, 1100, 1100, 1200]
    for seed, p in zip(SEEDS, parents):
        assert p['seed'] == seed and p['checkpoint_selected_by_training_only']
        assert p['history'][-1]['train_A'] == p['history'][-1]['train_B'] == 1.
    return parents, cuts, gauges


def prepare(frozen_role):
    parents, cuts, gauges = parent_spec()
    common = max(cuts)
    active = [r != frozen_role for r in range(2)]
    bundles = []
    for seed, parent in zip(SEEDS, parents):
        bundle = copy.deepcopy(parent)
        if parent['step'] < common:
            # Technical copies preserve the original batch4 CUDA arithmetic.
            # These BANDIT prefix updates are part of the registered science.
            models, opts, rngs = load_group([copy.deepcopy(parent) for _ in range(4)],
                                           [seed] * 4, active)
            _, tensors = data_for([seed] * 4)
            for _ in range(parent['step'], common):
                update(models, opts, rngs, tensors, active)
            for model in models:
                assert all(torch.equal(v[0], v[s]) for v in model.state_dict().values()
                           for s in range(1, 4)), 'Technical copies diverged'
            bundle = export_one(models, opts, rngs, 0, common, seed)
            del models, opts
            torch.cuda.empty_cache()
        bundles.append(bundle)
    return bundles, common, active, cuts, gauges


def technical():
    assert not OUT.exists()
    result_path = BASE / 'results/V195_WITHDRAW_TECHNICAL_REPLAY.json'
    assert not result_path.exists()
    # Independent finite-world payoff checks, before any intervention training.
    from v191_dual_neural_credit import environment_feedback
    fixture_rng = np.random.default_rng(195900)
    entries = 0
    for _ in range(6):
        p, n = 7, 17
        fa, fb, ua, ub = [torch.tensor(fixture_rng.integers(p, size=(2, n))) for _ in range(4)]
        perm = torch.tensor(np.stack([fixture_rng.permutation(n) for _ in range(2)]))
        ra, rb = realized_rewards(fa, fb, ua, ub, perm, p)
        _, _, expected_a, expected_b = environment_feedback(fa, fb, ua, ub, perm, p)
        assert torch.equal(ra, expected_a) and torch.equal(rb, expected_b)
        for s in range(2):
            for i in range(n):
                j = int(perm[s, i])
                correct = float((int(ua[s, i]) + int(ub[s, j])) % p ==
                                (int(fa[s, i]) + int(fb[s, j])) % p)
                assert float(ra[s, i]) == float(rb[s, j]) == correct
                entries += 2
    # Replay an ALREADY OBSERVED bandit history, not a new scientific arm.
    parent = BASE / 'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_BANDIT_IS'
    before = torch.load(parent / 'checkpoint_5000.pt', map_location='cpu', weights_only=False)
    expected = torch.load(parent / 'checkpoint_10000.pt', map_location='cpu', weights_only=False)
    models = [BatchedReceiver([2 * seed + r for seed in SEEDS], device='cuda') for r in range(2)]
    opts = []
    for r in range(2):
        models[r].load_state_dict(before['models'][r])
        opt = torch.optim.AdamW(models[r].parameters(), lr=.001, weight_decay=1., betas=(.9, .98))
        opt.load_state_dict(before['optimizers'][r])
        opts.append(opt)
    rngs = []
    for state in before['rng_states']:
        rng = np.random.default_rng(0)
        rng.bit_generator.state = copy.deepcopy(state)
        rngs.append(rng)
    _, tensors = data_for(SEEDS)
    block = time.monotonic()
    for step in range(5001, 10001):
        update(models, opts, rngs, tensors, [True, True])
        if step % 100 == 0:
            time.sleep(max(0., .4 - (time.monotonic() - block)))
            block = time.monotonic()
    comparisons = compare_tensors(expected['models'], [m.state_dict() for m in models], '/models')
    compare_tensors(expected['optimizers'], [o.state_dict() for o in opts], '/optimizers', comparisons)
    rng_same = expected['rng_states'] == [r.bit_generator.state for r in rngs]
    result = dict(historical_replay_only=True, new_scientific_training=False,
                  explicit_reward_entries_checked=entries, conditional_payoff_table_agreement=True,
                  replay_from=5000, replay_to=10000, family='PRIVATE_BANDIT_IS',
                  comparisons=comparisons, all_tensors_bit_identical=all(c['bit_identical'] for c in comparisons),
                  maximum_error=max(c['max_error'] for c in comparisons), RNG_states_identical=bool(rng_same),
                  checkpoint_sha256={str(k): hashlib.sha256((parent / f'checkpoint_{k}.pt').read_bytes()).hexdigest()
                                     for k in [5000, 10000]})
    result_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    assert result['all_tensors_bit_identical'] and rng_same, result
    print('V195_TECHNICAL_COMPLETE', json.dumps({k: v for k, v in result.items() if k != 'comparisons'}), flush=True)


def add_parent_gauge_metrics(rows, gauges, frozen_role):
    for s, row in enumerate(rows):
        for r, g in [(0, gauges[s]), (1, (-gauges[s]) % P)]:
            for split in ['train', 'test']:
                row[f'parent_gauge_{split}_'+('A' if r == 0 else 'B')] = float(row[f'{split}_error_histograms'][r][g])
        if frozen_role is not None:
            bound = max(row['test_error_histograms'][frozen_role])
            row['joint_test_upper_bound_from_frozen_peer'] = float(bound)
            assert row['test_joint_greedy'] <= bound + 1e-12


def train_arm(name, frozen_role):
    folder = OUT / name
    folder.mkdir(exist_ok=False)
    bundles, start, active, cuts, gauges = prepare(frozen_role)
    models, opts, rngs = load_group(bundles, SEEDS, active)
    arrays, tensors = data_for(SEEDS)
    frozen_before = None if frozen_role is None else {k: v.detach().clone() for k, v in models[frozen_role].state_dict().items()}
    torch.save(dict(bundles=bundles, common_step=start, individual_switch_steps=cuts,
                    parent_gauges_A=gauges, active=active), folder / 'initial_aligned_state.pt')
    histories = [[] for _ in SEEDS]
    streak_train, streak_test = [0] * 4, [0] * 4
    train_recovery, test_recovery = [None] * 4, [None] * 4
    frozen_checks = []
    block = time.monotonic()
    started = block
    for step in range(start + 1, END + 1):
        update(models, opts, rngs, tensors, active)
        if step % 100 == 0:
            rows = evaluate(models, arrays, 'cuda')
            add_parent_gauge_metrics(rows, gauges, frozen_role)
            for s, row in enumerate(rows):
                row['step'] = step
                histories[s].append(row)
                train_ok = row['train_joint_greedy'] >= .99
                test_ok = row['test_joint_greedy'] >= .95
                if frozen_role is not None:
                    role_name = 'B' if frozen_role == 0 else 'A'
                    train_ok = row[f'parent_gauge_train_{role_name}'] >= .99
                    test_ok = row[f'parent_gauge_test_{role_name}'] >= .95
                streak_train[s] = streak_train[s] + 1 if train_ok else 0
                streak_test[s] = streak_test[s] + 1 if test_ok else 0
                if train_recovery[s] is None and streak_train[s] >= 5:
                    train_recovery[s] = step
                if test_recovery[s] is None and streak_test[s] >= 5:
                    test_recovery[s] = step
            if step % 1000 == 0:
                metric = 'test_joint_greedy' if frozen_role is None else 'parent_gauge_test_'+('B' if frozen_role == 0 else 'A')
                print('V195', name, step, 'train_joint', round(np.mean([r['train_joint_greedy'] for r in rows]), 4),
                      'primary_test', round(np.mean([r[metric] for r in rows]), 4),
                      'sec', round(time.monotonic()-started, 1), flush=True)
            if step % 5000 == 0:
                if frozen_role is not None:
                    same = all(torch.equal(v, frozen_before[k]) for k, v in models[frozen_role].state_dict().items())
                    frozen_checks.append(dict(step=step, frozen_parameters_bit_identical=bool(same)))
                    assert same
                torch.save(dict(models=[m.state_dict() for m in models],
                                optimizers=[o.state_dict() if o is not None else None for o in opts],
                                step=step, rng_states=[r.bit_generator.state for r in rngs], histories=histories),
                           folder / f'checkpoint_{step}.pt')
                (folder / 'progress.json').write_text(json.dumps(dict(step=step, rows=rows), indent=2), encoding='utf-8')
            time.sleep(max(0., .4 - (time.monotonic()-block)))
            block = time.monotonic()
    results = []
    for s, seed in enumerate(SEEDS):
        final = histories[s][-1]
        if frozen_role is None:
            success = final['train_joint_greedy'] >= .99 and final['test_joint_greedy'] >= .95
            deficit = 1. - final['test_joint_greedy']
        else:
            field = 'parent_gauge_test_'+('B' if frozen_role == 0 else 'A')
            success = final[field] >= .95
            deficit = 1. - final[field]
        result = dict(seed=seed, arm=name, switch_step=cuts[s], parent_gauge_A=gauges[s], frozen_role=frozen_role,
                      final=final, history=histories[s], primary_block_passed=bool(success),
                      primary_deficit_against_FULL=float(deficit),
                      first_post_switch_sustained_train_step=train_recovery[s],
                      first_post_switch_sustained_test_step=test_recovery[s],
                      minimum_observed_post_switch_train_joint=float(min(r['train_joint_greedy'] for r in histories[s])))
        (folder / f'metrics_s{seed}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        results.append(result)
    (folder / 'FROZEN_PARAMETER_CHECKS.json').write_text(json.dumps(frozen_checks, indent=2), encoding='utf-8')
    count = sum(r['primary_block_passed'] for r in results)
    median_deficit = float(np.median([r['primary_deficit_against_FULL'] for r in results]))
    arm_summary = dict(arm=name, runs=[{k: v for k, v in r.items() if k != 'history'} for r in results],
                       primary_pass_count=count, median_deficit_against_FULL=median_deficit,
                       primary_criterion_passed=bool(count >= 3 and median_deficit <= .02))
    (folder / 'SUMMARY.json').write_text(json.dumps(arm_summary, indent=2), encoding='utf-8')
    del models, opts
    torch.cuda.empty_cache()
    return arm_summary


def run():
    receipt = json.loads((BASE / 'results/V195_WITHDRAW_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path, sha in receipt['source_sha256'].items():
        assert hashlib.sha256((BASE / path).read_bytes()).hexdigest() == sha, path
    for path, sha in receipt['binary_parent_sha256'].items():
        assert hashlib.sha256((BASE / path).read_bytes()).hexdigest() == sha, path
    technical_result = json.loads((BASE / 'results/V195_WITHDRAW_TECHNICAL_REPLAY.json').read_text(encoding='utf-8'))
    assert technical_result['all_tensors_bit_identical'] and technical_result['RNG_states_identical']
    OUT.mkdir(exist_ok=False)
    (OUT / 'MANIFEST.json').write_text(json.dumps(dict(preregistration=receipt, started_UTC=datetime.now(timezone.utc).isoformat(),
        reused_parent_histories=4, independent_new_roots=0, scalar_reward_only_after_switch=True,
        task_common_interests_and_prior_counterfactual_infrastructure_imposed=True,
        optimizer_moments_retained=True, torch=torch.__version__, device=torch.cuda.get_device_name(),
        epsilon=EPS, total_steps=END), indent=2), encoding='utf-8')
    main = train_arm(*ARMS[0])
    summaries = [main]
    cancelled = []
    if main['primary_criterion_passed']:
        cancelled = [name for name, _ in ARMS[1:]]
    else:
        for arm in ARMS[1:]:
            summaries.append(train_arm(*arm))
    summary = dict(arms=summaries, withdrawal_primary_passed=main['primary_criterion_passed'],
                   cancelled_unexecuted_conditions=cancelled, original_parent_histories=4,
                   independent_new_roots=0, new_institution_learning_accredited=False,
                   endogenous_formation_from_scratch_with_binary_feedback_demonstrated=False,
                   intrinsically_collective_grokking_accredited=False,
                   CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('V195_COMPLETE', json.dumps({k: v for k, v in summary.items() if k != 'arms'}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['technical', 'run'])
    args = parser.parse_args()
    print('LIMITS', apply_limits(2), flush=True)
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.cuda.set_per_process_memory_fraction(.35)
    {'technical': technical, 'run': run}[args.command]()
