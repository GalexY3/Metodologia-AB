"""Freeze V190 bytes before any scientific training; export for GitHub blobs."""
from pathlib import Path
import base64
import hashlib
import json

B = Path(__file__).resolve().parent
paths = [
    'PREREG_V190_LOSSY_MEMORIZATION_AND_GENERALIZATION.md',
    'v190_lossy_memorization.py', 'v188_private_conventions.py',
    'v187_classical_signaling.py', 'v185_collective_grokking.py',
    'research_resource_limits.py', 'v189_support_audit.py',
    'v189b_matched_context_graphs.py',
    'results/V190_TECHNICAL_AUDIT.json', 'results/V188_TECHNICAL_AUDIT.json',
    'results/V188_PRIVATE_CONVENTIONS/SUMMARY.json',
    'results/V189B_MATCHED_CONTEXTS/SUMMARY.json',
] + [f'results/V189B_MATCHED_CONTEXTS/pair_{i}.npz' for i in range(4)]
assert not (B / 'results/V190_LOSSY_MEMORIZATION').exists()
assert not (B / 'results/V190_SOURCE_PREREG.json').exists()
registration = dict(
    source_sha256={p: hashlib.sha256((B/p).read_bytes()).hexdigest() for p in paths},
    known_before_registration='V187/V188 completed; V189 and V189B mathematical/data construction only; V190 technical fixtures passed; no V190 scientific training',
    CPU_threads=2, GPU_memory_fraction_cap=.35,
    minimum_wall_seconds_per100_updates=.4,
)
manifest = 'results/V190_SOURCE_PREREG.json'
(B/manifest).write_text(json.dumps(registration, indent=2), encoding='utf-8')
exports = []
for p in paths + [manifest]:
    data = (B/p).read_bytes()
    binary = p.endswith('.npz')
    exports.append(dict(path=p, encoding='base64' if binary else 'utf-8',
                        content=base64.b64encode(data).decode() if binary else data.decode('utf-8')))
print(json.dumps(dict(registration=registration, files=exports)))
