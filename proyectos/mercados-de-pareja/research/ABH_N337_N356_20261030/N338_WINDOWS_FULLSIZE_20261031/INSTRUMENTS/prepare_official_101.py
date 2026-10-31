"""Freeze a single real ESBM N144 seed input BEFORE any outcomes (no simulate)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
DIR = ROOT / 'official_101'
TENSOR_NAMES = ['u_send', 'u_reply', 'u_hazard', 'u_expose', 'u_match']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if DIR.exists():
        raise SystemExit('INPUT_DIR_ALREADY_EXISTS')
    original = ROOT / 'esbm_dynamic.py'
    assert sha(original) == 'f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
    spec = importlib.util.spec_from_file_location('esbm_native_n338', original)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert (module.N, module.STEPS, module.K) == (144, 16, 7)
    data = module.people(101)
    DIR.mkdir()
    people = {key: data[key].tolist() for key in ['genders', 'scopes', 'norm', 'q', 'age']}
    path = DIR / 'people_101.json'
    path.write_text(json.dumps(people, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')
    files = {'people': {'name': path.name, 'sha256': sha(path), 'bytes': path.stat().st_size}}
    for name in TENSOR_NAMES:
        arr = data[name]
        assert arr.shape == (16, 144, 144) and arr.dtype == np.float64
        file = DIR / f'{name}_101.bin'
        file.write_bytes(arr.tobytes(order='C'))
        files[name] = {'name': file.name, 'sha256': sha(file), 'bytes': file.stat().st_size,
                       'shape': [16,144,144], 'dtype': '<f8'}
    manifest = {'schema': 'N338_OFFICIAL_SEED101_PREOUTCOME_INPUTS', 'seed': 101,
                'N': 144, 'T': 16, 'K': 7,
                'scenarios': ['mixed_random', 'private_rejection_learning'],
                'original_source_sha256': sha(original), 'producer_sha256': sha(__file__),
                'Python': sys.version.split()[0], 'NumPy': np.__version__,
                'files': files, 'status': 'INPUTS_FROZEN_NOT_SIMULATED'}
    out = ROOT / 'N338_INPUT_MANIFEST.json'
    if out.exists():
        raise SystemExit('MANIFEST_ALREADY_EXISTS')
    out.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('N338_INPUTS_FROZEN', sha(out), 'bytes', sum(x['bytes'] for x in files.values()))


if __name__ == '__main__':
    main()
