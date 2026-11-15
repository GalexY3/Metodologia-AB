"""Independent final forward pass, Cartesian metrics and intervention audit."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
from pathlib import Path
import copy
import hashlib
import json
import numpy as np
import torch
from audit_v192_numpy import audit
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
ROOT = B / 'results/V195_WITHDRAW_COUNTERFACTUAL'
SEEDS = list(range(192115, 192119))


def main():
    summary = json.loads((ROOT / 'SUMMARY.json').read_text(encoding='utf-8'))
    prereg = json.loads((B / 'results/V195_WITHDRAW_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    for path, sha in dict(prereg['source_sha256'], **prereg['binary_parent_sha256']).items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    output = B / 'results/V195_WITHDRAW_NUMPY_FINAL_AUDIT.json'
    assert not output.exists()
    audits, gauge_checks, frozen_checks, state_checks, gates = [], [], [], [], []
    p = 31
    aa, bb = np.indices((p, p))
    truth = (aa + bb) % p
    for arm in summary['arms']:
        name = arm['arm']
        folder = ROOT / name
        audits.append(audit('V195_'+name, 60000, folder / 'checkpoint_60000.pt'))
        final = torch.load(folder / 'checkpoint_60000.pt', map_location='cpu', weights_only=False)
        aligned = torch.load(folder / 'initial_aligned_state.pt', map_location='cpu', weights_only=False)
        successes, deficits = [], []
        for s, seed in enumerate(SEEDS):
            parent = torch.load(B/f'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/first_memorization_s{seed}.pt',
                                map_location='cpu', weights_only=False)
            row = final['histories'][s][-1]
            metrics = json.loads((folder/f'metrics_s{seed}.json').read_text(encoding='utf-8'))
            assert row == metrics['final'] == arm['runs'][s]['final']
            frozen_role = metrics['frozen_role']
            gauge = parent['history'][-1]['train_chosen_gauge_A']
            masks = np.load(B/f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz')['masks']
            for r, g in [(0, gauge), (1, (-gauge) % p)]:
                weights = {k: v[s].numpy().astype(np.float64) for k, v in final['models'][r].items()}
                hidden = weights['message'][:, None, :] + weights['context'][None, :, :]
                predicted = np.einsum('abh,hp->abp', hidden**2, weights['output']).argmax(2)
                correct = (predicted-truth) % p == g
                for split, mask in [('train', masks[r]), ('test', ~masks[r])]:
                    field = f'parent_gauge_{split}_'+('A' if r == 0 else 'B')
                    value = float(correct[mask].mean())
                    error = abs(value-row[field])
                    gauge_checks.append(dict(arm=name, seed=seed, field=field, reference=value,
                                             saved=row[field], error=error, passed=bool(error <= 1e-7)))
                if r == frozen_role:
                    assert final['optimizers'][r] is None
                    for checkpoint in sorted(folder.glob('checkpoint_*.pt')):
                        saved = torch.load(checkpoint, map_location='cpu', weights_only=False)
                        for key, value in parent['models'][r].items():
                            same = torch.equal(value, saved['models'][r][key][s:s+1])
                            frozen_checks.append(dict(arm=name, seed=seed, step=saved['step'], parameter=key,
                                                      bit_identical=bool(same)))
                            assert same, (name, seed, checkpoint.name, key)
                else:
                    for param_id, state in final['optimizers'][r]['state'].items():
                        assert int(state['step']) == 60000
                    for param_id, state in aligned['bundles'][s]['optimizers'][r]['state'].items():
                        assert int(state['step']) == 1200
                # Parents already at1200 receive no intervention prefix.
                if parent['step'] == 1200:
                    assert all(torch.equal(v, aligned['bundles'][s]['models'][r][k])
                               for k, v in parent['models'][r].items())
                    if r != frozen_role:
                        from v193_frozen_peer import compare_tensors
                        checks = compare_tensors(parent['optimizers'][r], aligned['bundles'][s]['optimizers'][r])
                        assert all(c['bit_identical'] for c in checks)
            rng = np.random.default_rng(0)
            rng.bit_generator.state = copy.deepcopy(parent['rng_state'])
            for _ in range(parent['step'], 1200):
                rng.random((2, 384)); rng.permutation(384)
            assert rng.bit_generator.state == aligned['bundles'][s]['rng_state']
            for _ in range(1200, 60000):
                rng.random((2, 384)); rng.permutation(384)
            assert rng.bit_generator.state == final['rng_states'][s]
            state_checks.append(dict(arm=name, seed=seed, original_cut=parent['step'],
                                     aligned_clock=1200, final_clock=60000, RNG_consumption_identical=True,
                                     unpadded_parent_weights_and_Adam_moments_retained=True))
            if frozen_role is None:
                success = row['train_joint_greedy'] >= .99 and row['test_joint_greedy'] >= .95
                deficit = 1-row['test_joint_greedy']
            else:
                value = row['parent_gauge_test_'+('B' if frozen_role == 0 else 'A')]
                success = value >= .95
                deficit = 1-value
            assert bool(success) == metrics['primary_block_passed']
            assert abs(deficit-metrics['primary_deficit_against_FULL']) < 1e-12
            successes.append(success); deficits.append(deficit)
        count, median = sum(successes), float(np.median(deficits))
        passed = bool(count >= 3 and median <= .02)
        assert count == arm['primary_pass_count'] and passed == arm['primary_criterion_passed']
        assert abs(median-arm['median_deficit_against_FULL']) < 1e-12
        gates.append(dict(arm=name, count=count, median_deficit=median, passed=passed))
    assert gates[0]['passed'] == summary['withdrawal_primary_passed']
    expected_controls = ['FREEZE_A_BANDIT_B', 'FREEZE_B_BANDIT_A']
    if gates[0]['passed']:
        assert summary['cancelled_unexecuted_conditions'] == expected_controls
        assert not any((ROOT/name).exists() for name in expected_controls)
    else:
        assert summary['cancelled_unexecuted_conditions'] == []
        assert [r['arm'] for r in summary['arms'][1:]] == expected_controls
    metric_checks = [c for a in audits for c in a['checks']] + gauge_checks
    failures = [c for c in metric_checks if not c['passed']]
    result = dict(independent_numpy_forward=True, explicit_Cartesian_game_enumeration=True,
                  scientific_new_roots=0, metric_checks=len(metric_checks), failures=failures,
                  max_error=max(c['error'] for c in metric_checks), audits=audits,
                  parent_gauge_checks=gauge_checks, frozen_parameter_checks=frozen_checks,
                  optimizer_and_RNG_checks=state_checks, primary_gates=gates,
                  conditional_control_execution_matches_preregistration=True,
                  frozen_scientific_sources_and_parents_unchanged=True)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    assert not failures, failures
    print(json.dumps({k: v for k, v in result.items() if k not in
        ['audits', 'parent_gauge_checks', 'frozen_parameter_checks', 'optimizer_and_RNG_checks']}), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    torch.set_num_threads(2)
    main()
