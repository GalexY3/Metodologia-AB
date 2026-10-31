"""Fail-closed exact field and matched-pair comparator for pre-frozen N337."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def diff(a, b, path='$'):
    if a is None or b is None:
        return None if a is b else {'path': path, 'a': a, 'b': b}
    if isinstance(a, bool) or isinstance(b, bool):
        return None if a is b else {'path': path, 'a': a, 'b': b}
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        error = abs(a - b)
        tolerance = 0 if isinstance(a, int) and isinstance(b, int) else 1e-9
        return None if math.isfinite(error) and error <= tolerance else {'path': path, 'a': a, 'b': b, 'error': error}
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return {'path': path + '.length', 'a': len(a), 'b': len(b)}
        for i, (x, y) in enumerate(zip(a, b)):
            mismatch = diff(x, y, f'{path}.{i}')
            if mismatch:
                return mismatch
        return None
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return {'path': path + '.keys', 'a': sorted(a), 'b': sorted(b)}
        for key in sorted(a):
            mismatch = diff(a[key], b[key], f'{path}.{key}')
            if mismatch:
                return mismatch
        return None
    return None if a == b else {'path': path, 'a': a, 'b': b}


def main():
    pyfile = ROOT / 'N337_PY_NATIVE.json'
    tsfile = ROOT / 'N337_TS_N207.json'
    a = json.loads(pyfile.read_text(encoding='utf-8'))['runs']
    b = json.loads(tsfile.read_text(encoding='utf-8'))['runs']
    assert len(a) == len(b) == 60
    cases = []
    for i, (pyrow, tsrow) in enumerate(zip(a, b)):
        assert pyrow['seed'] == tsrow['seed'] and pyrow['scenario'] == tsrow['scenario']
        status = tsrow['status']
        discrepancy = {'path': '$.ts_exception', 'a': None, 'b': tsrow.get('error')} if status != 'EXECUTED' else (
            diff(pyrow['formation_pairs_by_tick'], tsrow['formation_pairs_by_tick'], '$.formation_pairs_by_tick') or
            diff(pyrow['result'], tsrow['result'], '$.result'))
        cases.append({'seed': pyrow['seed'], 'scenario': pyrow['scenario'], 'status': status,
                      'first_difference': discrepancy, 'pair_ticks': len(pyrow['formation_pairs_by_tick']),
                      'ts_matching_status': tsrow.get('matching_status')})
    # Mutation negative control on a completed native report: one integer field must register a mismatch.
    mutated = json.loads(json.dumps(a[0]['result']))
    mutated['track'][0]['impressions'] += 1
    mutation = diff(a[0]['result'], mutated, '$.result')
    assert mutation and mutation['path'] == '$.result.track.0.impressions'
    report = {'schema': 'ABH_N337_PY_ORIGINAL_VS_TS_N207_SMALL_N',
              'population': 'Artificial N8 T6 K3, 6 seeds by 10 ESBM scenarios; NOT official N144',
              'original_python_sha256': sha(ROOT / 'esbm_dynamic.py'),
              'python_outcomes_sha256': sha(pyfile), 'typescript_outcomes_sha256': sha(tsfile),
              'cases': cases, 'passed_full_result_and_pairs': sum(x['first_difference'] is None for x in cases),
              'errors_or_differences': sum(x['first_difference'] is not None for x in cases),
              'mutation_detector': mutation, 'human_rows': 0, 'CT2': 7, 'STOP_R5_human': True,
              'historical_N237_TypeScript_executed': False}
    out = ROOT / 'N337_AUDIT.json'
    if out.exists():
        raise SystemExit('OUTPUT_ALREADY_EXISTS_FAIL_CLOSED')
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print('N337_AUDIT', report['passed_full_result_and_pairs'], '/60', 'differences', report['errors_or_differences'], sha(out))


if __name__ == '__main__':
    main()
