"""Input-only producer for a prospective original Python vs TypeScript test.

Generates no model outcomes. Never changes the historical ESBM source.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
SEEDS = [101, 211, 307, 401, 503, 601]
N, T, K = 8, 6, 3
SHOCKS = ('u_send', 'u_reply', 'u_hazard', 'u_expose', 'u_match')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    directory = ROOT / 'inputs'
    if directory.exists():
        raise SystemExit('INPUTS_ALREADY_EXIST_FAIL_CLOSED')
    directory.mkdir()
    manifest = {
        'schema': 'N337_SMALL_SHARED_INPUTS_V1',
        'n': N, 't': T, 'k': K, 'seeds': SEEDS,
        'shocks': SHOCKS,
        'generator_sha256': sha(__file__),
        'original_sha256': sha(ROOT / 'esbm_dynamic.py'),
        'python': sys.version.split()[0],
        'numpy': np.__version__,
        'platform': platform.platform(),
        'cases': [],
    }
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        genders = np.array(['F'] * 3 + ['M'] * 3 + ['X'] * 2)[rng.permutation(N)]
        scopes = np.array(['all'] * 4 + ['same'] * 2 + ['other'] * 2)[rng.permutation(N)]
        payload = {
            'seed': seed,
            'people': {
                'genders': genders.tolist(),
                'scopes': scopes.tolist(),
                'norm': rng.integers(0, 3, N).tolist(),
                'q': rng.random(N).tolist(),
                'age': rng.integers(19, 51, N).tolist(),
            },
            'shocks': {name: rng.random((T, N, N)).tolist() for name in SHOCKS},
        }
        target = directory / f'seed_{seed}.json'
        target.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n', encoding='utf-8')
        manifest['cases'].append({'seed': seed, 'path': target.name, 'sha256': sha(target), 'bytes': target.stat().st_size})
    out = ROOT / 'input_manifest.json'
    if out.exists():
        raise SystemExit('MANIFEST_EXISTS_FAIL_CLOSED')
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('INPUTS_ONLY_GENERATED', sha(out), len(manifest['cases']))


if __name__ == '__main__':
    main()
