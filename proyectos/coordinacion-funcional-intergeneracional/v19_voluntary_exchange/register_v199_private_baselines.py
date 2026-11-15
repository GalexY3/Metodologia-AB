"""Freeze protocol, algorithms, analysis rules and parent hashes; verify HTTP."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
from urllib.request import urlopen

B = Path(__file__).resolve().parent
R = B/'results'


def freeze():
    output = R/'V199_PRIVATE_BASELINES_SOURCE_PREREG.json'
    assert not output.exists() and not (R/'V199_PRIVATE_BASELINES').exists()
    technical = json.loads((R/'V199_PRIVATE_BASELINES_TECHNICAL.json').read_text(encoding='utf-8'))
    assert technical['scientific_training_executed'] is False
    assert technical['all_isolated_histories_and_observed_rewards_bit_identical']
    sources = ['v199_private_baselines.py', 'analyze_v199_private_baselines.py', 'register_v199_private_baselines.py',
               'PREREG_V199_PRIVATE_BASELINES.md', 'research_resource_limits.py', 'v197_tie_policy_audit.py',
               'results/V199_PRIVATE_BASELINES_TECHNICAL.json', 'literatura/V199_PRIVATE_BASELINES_PRIOR.json']
    parents = [f'results/V195_CORRELATED_EXPLORATION/V195_k{k}_{rule}_W32_G20_T8000.npz'
               for k in [4, 8, 12] for rule in ['UNANIMITY', 'MAJORITY']]
    registration = dict(created_UTC=datetime.now(timezone.utc).isoformat(),
        source_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in sources},
        binary_parent_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in parents},
        known_before_registration='V195-V198 complete; private baseline V199 synthetic technical fixtures only. No maintenance, formation or reversal scientific trajectories run.',
        new_formation_world_roots=192, borrowed_maintenance_parent_roots=True,
        methods_paired_within_world=True, CPU_NumBa_threads=2, GPU_used=False,
        primary_families=['H1_HYSTERETIC_MAINTENANCE', 'H2_HYSTERETIC_FORMATION'],
        primary_decision_rules_fixed_in_analysis_source=True, no_original_institution_claimed=True)
    output.write_text(json.dumps(registration, indent=2), encoding='utf-8')
    print(json.dumps(dict(frozen_sources=len(sources), binary_parents=len(parents), before_training=True)), flush=True)


def verify(commit, tree):
    output = R/'V199_PRIVATE_BASELINES_PREREG_RECEIPT.json'
    assert not output.exists() and not (R/'V199_PRIVATE_BASELINES').exists()
    registration = json.loads((R/'V199_PRIVATE_BASELINES_SOURCE_PREREG.json').read_text(encoding='utf-8'))
    checks = []
    for path in list(registration['source_sha256'])+['results/V199_PRIVATE_BASELINES_SOURCE_PREREG.json']:
        local = (B/path).read_bytes()
        url = f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{commit}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
        with urlopen(url, timeout=45) as response:
            remote = response.read()
        assert local == remote, path
        checks.append(dict(path=path, bytes=len(remote), sha256=hashlib.sha256(remote).hexdigest(), identical=True))
    for path, expected in registration['binary_parent_sha256'].items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == expected
    (R/'V199_PRIVATE_BASELINES_REMOTE_VERIFIED.json').write_text(json.dumps(dict(
        commit=commit, checks=checks, before_training=True), indent=2), encoding='utf-8')
    output.write_text(json.dumps(dict(registration, remote_commit=commit, remote_tree=tree,
        before_training=True, verified_UTC=datetime.now(timezone.utc).isoformat()), indent=2), encoding='utf-8')
    print(json.dumps(dict(commit=commit, HTTP_verified_files=len(checks), before_training=True)), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('command', choices=['freeze', 'verify'])
    p.add_argument('--commit'); p.add_argument('--tree'); a = p.parse_args()
    if a.command == 'freeze':
        freeze()
    else:
        assert a.commit and a.tree
        verify(a.commit, a.tree)
