"""Freeze the withdrawal protocol before any new intervention trajectory."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

B = Path(__file__).resolve().parent
assert not (B / 'results/V195_WITHDRAW_COUNTERFACTUAL').exists()
target = B / 'results/V195_WITHDRAW_SOURCE_PREREG.json'
assert not target.exists()
technical = json.loads((B / 'results/V195_WITHDRAW_TECHNICAL_REPLAY.json').read_text(encoding='utf-8'))
assert technical['all_tensors_bit_identical'] and technical['RNG_states_identical']
sources = [
    'PREREG_V195_WITHDRAW_COUNTERFACTUAL.md', 'v195_withdraw_counterfactual.py',
    'make_v195_withdraw_registration.py', 'verify_v195_withdraw_registration.py',
    'v193_frozen_peer.py', 'v192_dual_neural_learning.py', 'v191_dual_neural_credit.py',
    'v188_private_conventions.py', 'v187_classical_signaling.py', 'v185_collective_grokking.py',
    'research_resource_limits.py', 'results/V195_WITHDRAW_TECHNICAL_REPLAY.json',
    'results/V192_DUAL_NEURAL_LEARNING/SUMMARY.json', 'results/V193_FROZEN_PEER/SUMMARY.json',
    'docs/V194_REDUCCION_Y_PRIORIDAD_V195.md',
] + [f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{s}.npz' for s in range(192115, 192119)]
binaries = [f'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/first_memorization_s{s}.pt'
            for s in range(192115, 192119)]
binaries += [f'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_BANDIT_IS/checkpoint_{t}.pt' for t in [5000, 10000]]
registration = dict(created_UTC=datetime.now(timezone.utc).isoformat(),
    source_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in sources},
    binary_parent_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in binaries},
    binary_parents_previously_archived_in='research/V191_V194_20261115/EVIDENCE_PAYLOAD_SHA256.json',
    known_before_registration='V191-V194 complete and audited. Only historical V192 BANDIT 5000-10000 replay executed for V195 technical validation. No withdrawal prefixes or scientific continuations run.',
    original_parent_histories=4, new_independent_roots=0, GPU_memory_fraction_cap=.35,
    CPU_threads=2, minimum_wall_seconds_per100_updates=.4,
    parent_cuts=[1200, 1100, 1100, 1200], total_steps=60000,
    conditional_controls='Execute both frozen-peer BANDIT controls iff BOTH_BANDIT primary criterion fails.',
    local_control_gauge='Parent convention selected with training only; do not remap a unilateral gauge shift.')
target.write_text(json.dumps(registration, indent=2), encoding='utf-8')
print(json.dumps(dict(source_files=len(sources), binary_parents=len(binaries), before_training=True)), flush=True)
