"""Prespecified fixed-norm reproduction; no repair or execution of the outer GA."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
from numba import njit, prange
from research_resource_limits import apply_limits
from v182_yaman_kernel import lifetime, make_tape

BASE = Path(__file__).resolve().parent
OUT = BASE/'results/V184_PASTURE_REPLAY'


@njit(parallel=True, cache=True)
def evaluate(matrix, env, p3, p4, p10, uniforms):
    worlds, T = p3.shape[0], 5000
    curves = np.zeros((2, worlds, T))
    resources = np.zeros((2, worlds, T))
    fractions = np.zeros((2, worlds, 3))
    scores = np.zeros((2, worlds))
    symmetric = env[0] == env[1]
    for world in prange(worlds):
        for arm in range(1 if symmetric else 2):
            params = env.copy()
            if arm == 1:
                params[0], params[1] = env[1], env[0]
            r = lifetime(matrix, params, T, .1, 184115+world, 1,
                         p3[world], p4[world], p10[world], uniforms[world], True)
            curves[arm, world] = r[0]
            resources[arm, world] = r[1]
            scores[arm, world] = np.mean(r[0][-101:])
            for role in range(3):
                fractions[arm, world, role] = np.mean(r[3][role, -101:])/100.
        if symmetric:
            curves[1, world] = curves[0, world]
            resources[1, world] = resources[0, world]
            scores[1, world] = scores[0, world]
            fractions[1, world] = fractions[0, world]
    return curves, resources, fractions, scores


def run():
    receipt = json.loads((BASE/'results/V184_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_new_scientific_lifetimes'] and receipt['remote_commit']
    for path, sha in receipt['source_sha256'].items():
        assert hashlib.sha256((BASE/path).read_bytes()).hexdigest() == sha, path
    parity = json.loads((BASE/'results/V182_OCTAVE_VALIDATION/parity_audit.json').read_text(encoding='utf-8'))
    assert not parity['failures'] and len(parity['checks']) == 51
    OUT.mkdir(exist_ok=True)
    stamp = OUT/'SOURCE_MANIFEST.json'
    if stamp.exists():
        assert json.loads(stamp.read_text(encoding='utf-8')) == receipt
    else:
        stamp.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    archive = json.loads((BASE/'results/V182_YAMAN_ARCHIVE_AUDIT/archive_audit.json').read_text(encoding='utf-8'))
    rows = [r for r in archive['rows'] if r['file'].startswith('common pasture/')
            and r['lambda_complexity'] in (0., .2)]
    assert len(rows) == 300
    tapes = [make_tape(5000, seed) for seed in range(184115, 184119)]
    p3, p4, p10, uniforms = (np.stack([t[i] for t in tapes]) for i in range(4))
    del tapes
    started = time.monotonic()
    for index, row in enumerate(rows):
        name = f'norm_{index:03d}'
        target = OUT/(name+'.json')
        if target.exists():
            continue
        curves, resources, fractions, scores = evaluate(np.array(row['norm']), np.array(row['env'], dtype=float),
                                                        p3, p4, p10, uniforms)
        assert np.all(np.isfinite(curves)) and np.min(resources) >= 0
        symmetric = row['env'][0] == row['env'][1]
        if symmetric:
            assert np.array_equal(curves[0], curves[1]) and np.array_equal(resources[0], resources[1])
        np.savez_compressed(OUT/(name+'.npz'), curves=curves, resources=resources,
                            role_fractions=fractions, scores=scores)
        item = dict(index=index, original_source=row, arms=['RELEASE', 'SWAPPED'],
                    symmetric_reused=bool(symmetric), unique_lifetime_evaluations=4 if symmetric else 8,
                    life_seeds=list(range(184115, 184119)), scores=scores.tolist(),
                    role_fractions=fractions.tolist(), tail_resource=resources[:, :, -101:].mean(axis=2).tolist())
        target.write_text(json.dumps(item, indent=2), encoding='utf-8')
        if index % 10 == 0 or index == 299:
            print('COMPLETED_NORMS', index+1, '/', len(rows), 'elapsed_sec', round(time.monotonic()-started, 1), flush=True)
    analyze()


def analyze():
    rows = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(OUT.glob('norm_*.json'))]
    assert len(rows) == 300
    asymmetric = [r for r in rows if not r['symmetric_reused']]
    assert len(asymmetric) == 120
    original = np.array([r['original_source']['tail_mean'] for r in asymmetric])
    scores = np.array([r['scores'] for r in asymmetric]).mean(axis=2)
    rmse = np.sqrt(np.mean((scores-original[:, None])**2, axis=0))
    difference = float(np.mean(np.abs(scores[:, 0]-scores[:, 1])))
    favored = 'RELEASE' if rmse[0] < rmse[1] else 'SWAPPED'
    strong = float(min(rmse)) < .5*float(max(rmse)) and difference >= 1.
    groups = {}
    for r in rows:
        source = r['original_source']
        key = (source['lambda_complexity'], tuple(source['env']))
        groups.setdefault(key, []).append(r)
    summaries = []
    for key, group in sorted(groups.items()):
        s = np.array([r['scores'] for r in group])
        summaries.append(dict(lambda_complexity=key[0], env=key[1], n=30,
                              archived_mean=float(np.mean([r['original_source']['tail_mean'] for r in group])),
                              release_mean=float(np.mean(s[:, 0])), swapped_mean=float(np.mean(s[:, 1]))))
    result = dict(descriptive_reproduction=True, archive_fits=300, asymmetric_fits=120,
                  unique_lifetime_evaluations=sum(r['unique_lifetime_evaluations'] for r in rows),
                  original_master_seed_blocks=30, RMSE_release=float(rmse[0]), RMSE_swapped=float(rmse[1]),
                  mean_absolute_mapping_difference=difference, favored_mapping=favored,
                  strong_correspondence_gate=bool(strong), context_summaries=summaries,
                  exact_original_generator_identified=False, new_institution_learned=False,
                  original_GA_repaired_or_retrained=False, CT2_historical=61, N2=0, N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['run', 'analyze'])
    args = p.parse_args()
    print('LIMITS', apply_limits(3), flush=True)
    {'run':run, 'analyze':analyze}[args.command]()
