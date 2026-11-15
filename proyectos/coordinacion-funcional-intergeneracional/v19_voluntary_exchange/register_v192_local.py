"""Prepare byte-exact V192 registration; no scientific training."""
from pathlib import Path
import base64
import hashlib
import json

B=Path(__file__).resolve().parent
assert not (B/'results/V192_DUAL_NEURAL_LEARNING').exists()
paths=['PREREG_V192_DUAL_NEURAL_PRIVATE_CREDIT.md','docs/V191_DUAL_NEURAL_IDENTIFICATION.md',
       'v191_dual_neural_credit.py','v191b_dual_gpu_fixture.py','v192_dual_neural_learning.py',
       'v188_private_conventions.py','v187_classical_signaling.py','v185_collective_grokking.py',
       'research_resource_limits.py','results/V191_TECHNICAL_AUDIT.json','results/V191B_GPU_TECHNICAL_AUDIT.json']
paths += [p.relative_to(B).as_posix() for p in sorted((B/'results/V191_DUAL_NEURAL_AUDIT_V2').glob('*.npz'))]
registration=dict(source_sha256={p:hashlib.sha256((B/p).read_bytes()).hexdigest() for p in paths},
    known_before_registration='V187–V190 published and architecture retired. V191 mathematical/GPU synthetic fixtures passed; data coverage corrected before training. No V192 scientific training.',
    GPU_memory_fraction_cap=.35,CPU_threads=2,minimum_wall_seconds_per100_updates=.4)
manifest='results/V192_SOURCE_PREREG.json';assert not (B/manifest).exists()
(B/manifest).write_text(json.dumps(registration,indent=2),encoding='utf-8')
files=[]
for path in paths+[manifest]:
    data=(B/path).read_bytes();binary=path.endswith('.npz')
    files.append(dict(path=path,encoding='base64' if binary else 'utf-8',
                      content=base64.b64encode(data).decode() if binary else data.decode('utf-8')))
print(json.dumps(dict(registration=registration,files=files)))
