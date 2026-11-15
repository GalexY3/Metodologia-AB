"""Preregistered paired hazard-timing intervention on all original frozen norms."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
from numba import njit, prange
from scipy.io import loadmat
from research_resource_limits import apply_limits
from v182_yaman_kernel import make_tape
from v183_yaman_timing_kernel import lifetime_timing

BASE = Path(__file__).resolve().parent
OUT = BASE / 'results/V183_HAZARD_TIMING'
SOURCES = ['PREREG_V183_YAMAN_HAZARD_TIMING.md', 'v182_yaman_kernel.py',
           'v183_build_kernel.py', 'v183_yaman_timing_kernel.py', 'v183_run_timing.py',
           'research_resource_limits.py']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def technical_gate():
    checks = []
    directory = BASE/'results/V182_OCTAVE_VALIDATION'
    original_audit = json.loads((directory/'parity_audit.json').read_text(encoding='utf-8'))
    assert len(original_audit['checks']) == 51 and not original_audit['failures']
    for fixture in sorted(directory.glob('fixture_*.mat')):
        d = loadmat(fixture, squeeze_me=True)
        tapes = tuple(np.asarray(d[k], dtype=np.int64 if k != 'uniforms' else float)
                      for k in ['p3', 'p4', 'p10', 'uniforms'])
        game, T = int(d['game']), int(d['T'])
        got = lifetime_timing(np.array(d['matrix']), np.array(d['env']), T, .1, 183000, game, *tapes, True, False)
        original = loadmat(directory/('output_'+fixture.name), simplify_cells=True)
        r = original['results']
        expected = [r['phi'], r['wasteTrend' if game == 0 else 'resourceTrend'],
                    r.get('advTrend', np.zeros(T)), r['roleTrend'], r['selection']-1,
                    r['used'], r['nRew'], r['nPun'], original['counters']]
        for index, value in enumerate(expected):
            error = float(np.max(np.abs(np.asarray(got[index])-np.asarray(value))))
            tolerance = 1e-10 if index in (0, 1) else (1e-14 if index == 5 else 0)
            checks.append(dict(fixture=fixture.name, field=index, error=error,
                               tolerance=tolerance, passed=error <= tolerance))
        checks.append(dict(fixture=fixture.name, field='conservation_and_identity',
                           error=float(max(got[11], got[12])), tolerance=1e-10,
                           passed=max(got[11], got[12]) <= 1e-10))
        if game == 0:
            # A fixed technical fixture, not a selected scientific outcome.
            left = lifetime_timing(np.array(d['matrix']), np.array([.5, 0]), T, .1, 1, game, *tapes, True, False)
            right = lifetime_timing(np.array(d['matrix']), np.array([.5, 0]), T, .1, 1, game, *tapes, True, True)
            error = max(float(np.max(np.abs(np.asarray(a)-np.asarray(b)))) for a, b in zip(left, right))
            checks.append(dict(fixture=fixture.name, field='zero_hazard_negative_control',
                               error=error, tolerance=1e-10, passed=error <= 1e-10))
    failures = [c for c in checks if not c['passed']]
    report = dict(checks=checks, failures=failures, new_scientific_lifetimes_executed=False,
                  fixed_technical_fixtures_only=True)
    (BASE/'results/V183_TECHNICAL_GATE.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('TECHNICAL_GATE', len(checks), 'checks', len(failures), 'failures', flush=True)
    assert not failures, failures


@njit(parallel=True, cache=True)
def evaluate_norm(matrix, env, p3, p4, p10, uniforms):
    worlds = p3.shape[0]
    T = 500
    curves = np.zeros((2, worlds, T))
    # R_tail, direct material delta, its analytic expectation, conservation,
    # identity residual, nRew, nPun, zero-hazard path discrepancy.
    metrics = np.zeros((2, worlds, 8))
    fractions = np.zeros((2, worlds, 4))
    for world in prange(worlds):
        first = lifetime_timing(matrix, env, T, .1, 183115+world, 0,
                                p3[world], p4[world], p10[world], uniforms[world], True, False)
        second = lifetime_timing(matrix, env, T, .1, 183115+world, 0,
                                 p3[world], p4[world], p10[world], uniforms[world], True, True)
        error = 0.
        if env[1] == 0:
            error = max(np.max(np.abs(first[0]-second[0])), np.max(np.abs(first[1]-second[1])),
                        np.max(np.abs(first[2]-second[2])), np.max(np.abs(first[3]-second[3])),
                        np.max(np.abs(first[4]-second[4])), np.max(np.abs(first[5]-second[5])),
                        abs(first[6]-second[6]), abs(first[7]-second[7]), np.max(np.abs(first[8]-second[8])))
        for arm in range(2):
            result = first if arm == 0 else second
            curves[arm, world] = result[0]
            metrics[arm, world, 0] = np.mean(result[0][-101:])
            metrics[arm, world, 1] = np.mean(result[9][-101:])
            metrics[arm, world, 2] = np.mean(result[10][-101:])
            metrics[arm, world, 3] = result[11]
            metrics[arm, world, 4] = result[12]
            metrics[arm, world, 5] = result[6]
            metrics[arm, world, 6] = result[7]
            metrics[arm, world, 7] = error
            for role in range(4):
                fractions[arm, world, role] = np.mean(result[3][role, -101:])/100.
    return curves, metrics, fractions


def run():
    receipt = json.loads((BASE/'results/V183_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['remote_commit'] and receipt['before_new_scientific_lifetimes']
    for path, expected in receipt['source_sha256'].items():
        assert digest(BASE/path) == expected, path
    gate = json.loads((BASE/'results/V183_TECHNICAL_GATE.json').read_text(encoding='utf-8'))
    assert not gate['failures']
    OUT.mkdir(parents=True, exist_ok=True)
    record = OUT/'SOURCE_MANIFEST.json'
    if record.exists():
        assert json.loads(record.read_text(encoding='utf-8')) == receipt
    else:
        record.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    data = json.loads((BASE/'results/V182_YAMAN_ARCHIVE_AUDIT/archive_audit.json').read_text(encoding='utf-8'))
    rows = [r for r in data['rows'] if r['file'].startswith('settlement maintenance/')
            and r['lambda_complexity'] in (0., .2)]
    assert len(rows) == 300
    tapes = [make_tape(500, seed) for seed in range(183115, 183123)]
    p3, p4, p10, uniforms = (np.stack([t[i] for t in tapes]) for i in range(4))
    started = time.monotonic()
    for index, row in enumerate(rows):
        name = f"norm_{index:03d}"
        destination = OUT/(name+'.json')
        if destination.exists():
            continue
        curves, metrics, fractions = evaluate_norm(np.asarray(row['norm']), np.asarray(row['env'], dtype=float),
                                                   p3, p4, p10, uniforms)
        assert np.max(metrics[:, :, 3:5]) <= 1e-10, 'Conservation / identity failure'
        if row['env'][1] == 0:
            assert np.max(metrics[:, :, 7]) <= 1e-10, 'Zero-hazard causal control failed'
        np.savez_compressed(OUT/(name+'.npz'), curves=curves, metrics=metrics, role_fractions=fractions)
        item = dict(index=index, original_source=row, arms=['ORIGINAL', 'ATTACK_FIRST'],
                    new_lifetime_seeds=list(range(183115, 183123)), metrics=metrics.tolist(),
                    metric_names=['tail_mean_101', 'material_delta_actual', 'material_delta_expected',
                                  'max_transfer_conservation_error', 'max_conditional_identity_error',
                                  'n_rewards', 'n_punishments', 'zero_hazard_path_error'],
                    tail_mean_by_arm=np.mean(metrics[:, :, 0], axis=1).tolist(),
                    role_fractions=fractions.tolist())
        destination.write_text(json.dumps(item, indent=2), encoding='utf-8')
        if index % 10 == 0 or index == len(rows)-1:
            print('COMPLETED_NORMS', index+1, '/', len(rows), 'elapsed_sec', round(time.monotonic()-started, 1), flush=True)
    analyze()


def analyze():
    rows = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(OUT.glob('norm_*.json'))]
    assert len(rows) == 300
    groups = {}
    for row in rows:
        original = row['original_source']
        key = (original['lambda_complexity'], tuple(original['env']))
        groups.setdefault(key, []).append(row)
    summaries, differences = [], []
    for key, values in sorted(groups.items()):
        values.sort(key=lambda r:r['original_source']['seed'])
        assert [r['original_source']['seed'] for r in values] == list(range(1, 31))
        metrics = np.array([r['metrics'] for r in values])
        delta = metrics[:, 0, :, 0]-metrics[:, 1, :, 0]
        item = dict(lambda_complexity=key[0], env=key[1], n_original_seed_blocks=30,
                    original_mean=float(np.mean(metrics[:, 0, :, 0])),
                    attack_first_mean=float(np.mean(metrics[:, 1, :, 0])),
                    delta_mean=float(np.mean(delta)), process_delta=delta.mean(axis=1).tolist(),
                    immediate_material_delta=float(np.mean(metrics[:, 0, :, 1])),
                    immediate_material_expected=float(np.mean(metrics[:, 0, :, 2])),
                    archived_training_mean=float(np.mean([r['original_source']['tail_mean'] for r in values])))
        summaries.append(item)
        if key[1][1] > 0:
            differences.append(delta)
    d = np.stack(differences)  # six contexts x 30 original seeds x 8 new lives
    assert d.shape == (6, 30, 8)
    rng = np.random.default_rng(183999)
    boot = np.empty(10000)
    for i in range(len(boot)):
        master = rng.integers(0, 30, size=30)
        world = rng.integers(0, 8, size=8)
        boot[i] = np.mean(d[:, master, :][:, :, world])
    ci = np.quantile(boot, [.025, .975]).tolist()
    effect = float(d.mean())
    gate = effect >= .25 and ci[0] > 0
    report = dict(primary_effect=effect, hierarchical_bootstrap_CI95=ci, primary_gate_passed=bool(gate),
                  prespecified_margin=.25, context_summaries=summaries, original_norms=300,
                  original_master_seed_blocks=30, new_lives_per_norm_per_arm=8,
                  total_lifetime_evaluations=4800, norm_reoptimization_executed=False,
                  institution_learned_by_private_agents=False, CT2_historical_unchanged=61,
                  N2=0, N3=0, bootstrap_seed=183999,
                  direct_material_delta_is_not_a_full_trajectory_decomposition=True)
    (OUT/'SUMMARY.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['technical-gate', 'run', 'analyze'])
    args = parser.parse_args()
    print('LIMITS', apply_limits(3), flush=True)
    {'technical-gate':technical_gate, 'run':run, 'analyze':analyze}[args.command]()
