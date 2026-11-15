"""Freeze or remotely verify the mean-drift diagnostic before running it."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
from urllib.request import urlopen

B = Path(__file__).resolve().parent
R = B/'results'


def freeze():
    target = R/'V198_EXPECTED_DRIFT_SOURCE_PREREG.json'
    assert not target.exists() and not (R/'V198_VOTING_EXPECTED_DRIFT').exists()
    technical = json.loads((R/'V198_EXPECTED_DRIFT_TECHNICAL.json').read_text(encoding='utf-8'))
    assert technical['no_scientific_trajectory_executed'] and technical['maximum_error'] < 2e-11
    paths = ['v198_voting_expected_drift.py', 'v197_tie_policy_audit.py',
             'register_v198_expected_drift.py', 'research_resource_limits.py',
             'PREREG_V198_VOTING_EXPECTED_DRIFT.md', 'results/V198_EXPECTED_DRIFT_TECHNICAL.json',
             'v195_joint_signal_policy_exploration.py', 'v196_plastic_no_pulse_maintenance.py']
    parents = [f'results/V195_CORRELATED_EXPLORATION/V195_k{k}_{rule}_W32_G20_T8000.npz'
               for k in [4, 8, 12] for rule in ['UNANIMITY', 'MAJORITY']]
    parents += ['results/V197_TIE_POLICY_AUDIT.json']
    result = dict(created_UTC=datetime.now(timezone.utc).isoformat(),
        source_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in paths},
        binary_parent_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in parents},
        known_before_registration='V195-V196 voting complete; V197 corrected frozen endpoints. No real-parent mean-drift trajectories executed. V198 synthetic fixtures only.',
        CPU_NumBa_threads=2, GPU_used=False, independent_new_roots=0,
        operator_is_oracle_diagnostic=True, steps=8000)
    target.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(dict(frozen_source_files=len(paths), fixed_parent_files=len(parents))), flush=True)


def verify(commit, tree):
    receipt_path = R/'V198_EXPECTED_DRIFT_PREREG_RECEIPT.json'
    assert not receipt_path.exists() and not (R/'V198_VOTING_EXPECTED_DRIFT').exists()
    registration = json.loads((R/'V198_EXPECTED_DRIFT_SOURCE_PREREG.json').read_text(encoding='utf-8'))
    checks = []
    for path in list(registration['source_sha256'])+['results/V198_EXPECTED_DRIFT_SOURCE_PREREG.json']:
        local = (B/path).read_bytes()
        url = f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{commit}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
        with urlopen(url, timeout=45) as response:
            remote = response.read()
        assert remote == local, path
        checks.append(dict(path=path, bytes=len(remote), sha256=hashlib.sha256(remote).hexdigest(), identical=True))
    for path, sha in registration['binary_parent_sha256'].items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    (R/'V198_EXPECTED_DRIFT_REMOTE_VERIFIED.json').write_text(json.dumps(dict(commit=commit, checks=checks,
        before_training=True), indent=2), encoding='utf-8')
    receipt_path.write_text(json.dumps(dict(registration, remote_commit=commit, remote_tree=tree,
        before_training=True, verified_UTC=datetime.now(timezone.utc).isoformat()), indent=2), encoding='utf-8')
    print(json.dumps(dict(commit=commit, HTTP_verified_files=len(checks), before_training=True)), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['freeze', 'verify'])
    p.add_argument('--commit')
    p.add_argument('--tree')
    args = p.parse_args()
    if args.command == 'freeze':
        freeze()
    else:
        assert args.commit and args.tree
        verify(args.commit, args.tree)
