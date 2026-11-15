"""Freeze the missing binary-feedback competence control before training."""
from pathlib import Path
import hashlib
import json

B=Path(__file__).resolve().parent
assert not (B/'results/V194_ORACLE_BANDIT').exists()
paths=['PREREG_V194_ORACLE_BANDIT_CAPABILITY.md','v194_oracle_bandit_control.py','v192_dual_neural_learning.py',
       'v191_dual_neural_credit.py','v188_private_conventions.py','v187_classical_signaling.py',
       'v185_collective_grokking.py','research_resource_limits.py','results/V194_TECHNICAL_AUDIT.json',
       'results/V192_DUAL_NEURAL_LEARNING/SUMMARY.json']
paths += [f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz' for seed in range(192115,192119)]
registration=dict(source_sha256={p:hashlib.sha256((B/p).read_bytes()).hexdigest() for p in paths},
    known_before_registration='V192 complete, V193 registered causal arms running, no V194 training. Missing bandit-oracle capability control identified before attribution to endogenous peers.',
    GPU_memory_fraction_cap=.35,CPU_threads=2,minimum_wall_seconds_per100_updates=.4)
p=B/'results/V194_SOURCE_PREREG.json';assert not p.exists()
p.write_text(json.dumps(registration,indent=2),encoding='utf-8')
exports=['PREREG_V194_ORACLE_BANDIT_CAPABILITY.md','v194_oracle_bandit_control.py','results/V194_TECHNICAL_AUDIT.json','results/V194_SOURCE_PREREG.json']
print(json.dumps(dict(registration=registration,files=[dict(path=s,content=(B/s).read_bytes().decode('utf-8'),encoding='utf-8') for s in exports])))
