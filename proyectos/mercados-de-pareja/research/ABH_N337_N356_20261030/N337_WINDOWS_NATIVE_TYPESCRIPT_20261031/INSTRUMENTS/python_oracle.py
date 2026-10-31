"""Run the UNMODIFIED ESBM simulate() with a smaller injected synthetic fixture.

Only module globals N/T/K and the input supplier are replaced; the source file
and simulate() function body remain byte-identical to the archived original.
Captures the NetworkX matching pair identities without changing its return.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SEEDS = [101, 211, 307, 401, 503, 601]
SCENARIOS = [
    'mixed_random', 'heterosexual_restricted', 'institutional_segregation',
    'explicit_norm_preference', 'popularity_ranking', 'visibility_balancing',
    'private_rejection_learning', 'public_rejection_signal',
    'longer_partnerships', 'shorter_partnerships',
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(ROOT / 'esbm_dynamic.py') == 'f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
    spec = importlib.util.spec_from_file_location('esbm_native_n337', ROOT / 'esbm_dynamic.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.N, mod.STEPS, mod.K = 8, 6, 3
    original_match = mod.nx.algorithms.matching.max_weight_matching
    results = []
    for seed in SEEDS:
        data_path = ROOT / 'inputs' / f'seed_{seed}.json'
        raw = json.loads(data_path.read_text(encoding='utf-8'))
        p = {key: np.asarray(value) for key, value in raw['people'].items()}
        p.update({key: np.asarray(value, dtype=np.float64) for key, value in raw['shocks'].items()})
        mod.people = lambda _seed, fixture=p: fixture
        for name in SCENARIOS:
            observed_pairs = []

            def hooked(graph, *args, **kwargs):
                pairs = original_match(graph, *args, **kwargs)
                observed_pairs.append(sorted([sorted([int(a), int(b)]) for a, b in pairs]))
                return pairs

            mod.nx.algorithms.matching.max_weight_matching = hooked
            try:
                row = mod.simulate(seed, name, mod.SCENARIOS[name])
            finally:
                mod.nx.algorithms.matching.max_weight_matching = original_match
            assert len(observed_pairs) == mod.STEPS, ('UNEXPECTED_MATCH_CALL_COUNT', seed, name)
            results.append({'seed': seed, 'scenario': name, 'result': row, 'formation_pairs_by_tick': observed_pairs})
    dest = ROOT / 'N337_PY_NATIVE.json'
    if dest.exists():
        raise SystemExit('OUTPUT_ALREADY_EXISTS_FAIL_CLOSED')
    dest.write_text(json.dumps({'schema': 'N337_PY_ORIGINAL_SMALL_INPUT', 'runs': results}, allow_nan=False, indent=2) + '\n', encoding='utf-8')
    print('ORIGINAL_PY_EXECUTED', len(results), sha(dest))


if __name__ == '__main__':
    main()
