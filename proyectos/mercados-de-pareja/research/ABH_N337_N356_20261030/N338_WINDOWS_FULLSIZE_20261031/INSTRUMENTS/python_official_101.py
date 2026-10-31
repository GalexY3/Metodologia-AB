"""Run unmodified original Python simulate() on frozen official N144 seed101 inputs."""
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
NAMES = ['mixed_random', 'private_rejection_learning']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(ROOT / 'esbm_dynamic.py') == 'f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
    manifest_path = ROOT / 'N338_INPUT_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['status'] == 'INPUTS_FROZEN_NOT_SIMULATED'
    spec = importlib.util.spec_from_file_location('esbm_official_n338', ROOT / 'esbm_dynamic.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert (mod.N, mod.STEPS, mod.K) == (144, 16, 7)
    fixture = mod.people(101)
    base = ROOT / 'official_101'
    for name in ['u_send', 'u_reply', 'u_hazard', 'u_expose', 'u_match']:
        file = base / manifest['files'][name]['name']
        assert sha(file) == manifest['files'][name]['sha256']
        assert np.array_equal(fixture[name], np.fromfile(file, dtype='<f8').reshape((16,144,144)))
    assert json.loads((base / 'people_101.json').read_text(encoding='utf-8')) == \
        {k: fixture[k].tolist() for k in ['genders', 'scopes', 'norm', 'q', 'age']}
    original_match = mod.nx.algorithms.matching.max_weight_matching
    results = []
    for name in NAMES:
        matches = []

        def logged(graph, *args, **kwargs):
            pairs = original_match(graph, *args, **kwargs)
            matches.append(sorted([sorted([int(a), int(b)]) for a, b in pairs]))
            return pairs

        mod.nx.algorithms.matching.max_weight_matching = logged
        try:
            row = mod.simulate(101, name, mod.SCENARIOS[name])
        finally:
            mod.nx.algorithms.matching.max_weight_matching = original_match
        assert len(matches) == 16
        results.append({'seed':101,'scenario':name,'result':row,'formation_pairs_by_tick':matches})
    outfile = ROOT / 'N338_PY_OFFICIAL.json'
    if outfile.exists():
        raise SystemExit('OUTPUT_PREEXISTS')
    outfile.write_text(json.dumps({'schema':'N338_PY_OFFICIAL','runs':results},indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('N338_PY_ORIGINAL_OFFICIAL',len(results), sha(outfile))


if __name__ == '__main__':
    main()
