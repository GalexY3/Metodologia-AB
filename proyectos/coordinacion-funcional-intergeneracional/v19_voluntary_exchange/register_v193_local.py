"""Hash all parents, export small registration files; binary parents stay hashed."""
from pathlib import Path
import base64
import hashlib
import json

B=Path(__file__).resolve().parent
assert not (B/'results/V193_FROZEN_PEER').exists()
paths=['PREREG_V193_FROZEN_PEER_CAUSAL_TEST.md','v193_frozen_peer.py','v192_dual_neural_learning.py',
       'v191_dual_neural_credit.py','v188_private_conventions.py','v187_classical_signaling.py',
       'v185_collective_grokking.py','research_resource_limits.py','results/V193_TECHNICAL_REPLAY.json',
       'results/V192_DUAL_NEURAL_LEARNING/SUMMARY.json','results/V192_NUMPY_FINAL_AUDIT.json',
       'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/checkpoint_5000.pt']
paths += [f'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/first_memorization_s{seed}.pt' for seed in range(192115,192119)]
paths += [f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz' for seed in range(192115,192119)]
registration=dict(source_sha256={p:hashlib.sha256((B/p).read_bytes()).hexdigest() for p in paths},
    known_before_registration='V192 complete;4 PRIVATE_FULL late candidates;final NumPy audit96checks passed;V193 historical replay bit identical. No scientific freeze continuations executed.',
    binary_parent_hashes_preregistered=True,binary_parents_to_be_delivered_with_results=True,
    GPU_memory_fraction_cap=.35,CPU_threads=2,minimum_wall_seconds_per100_updates=.4)
manifest='results/V193_SOURCE_PREREG.json';assert not (B/manifest).exists()
(B/manifest).write_text(json.dumps(registration,indent=2),encoding='utf-8')
files=[]
for path in paths+[manifest]:
    if path.endswith('.pt'):continue
    data=(B/path).read_bytes();binary=path.endswith('.npz')
    files.append(dict(path=path,encoding='base64' if binary else 'utf-8',
                      content=base64.b64encode(data).decode() if binary else data.decode('utf-8')))
print(json.dumps(dict(registration=registration,files=files)))
