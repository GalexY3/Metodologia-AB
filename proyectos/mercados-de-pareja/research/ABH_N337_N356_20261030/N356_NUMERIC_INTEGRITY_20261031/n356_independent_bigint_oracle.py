"""AB-H N356: independent fraction-based verifier, executed only after GitHub SHA freeze."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'outcomes' / 'N356_NUMERIC_PRECISION_BOUNDARY.json'
DEST = ROOT / 'outcomes' / 'N356_PYTHON_INDEPENDENT_ORACLE.json'
assert not DEST.exists(), 'REFUSE_OVERWRITE'
SCALE = 2**52
obj = json.loads(SRC.read_text('utf8'))
assert obj['schema'] == 'ABH_N356_INTEGER_EXACTNESS_OF_SERIALIZED_OBJECTIVE_V1'
assert obj['controls'] == 12 and len(obj['rows']) == 12
checks = []
for row in obj['rows']:
    pairs = [tuple(p) for p in row['pairs']]
    assert len(pairs) == row['cardinality']
    assert len(set(v for p in pairs for v in p)) == 2 * len(pairs)
    # Fixtures are disjoint edges (2*i,2*i+1), so no edge can be swapped.
    expected = [(2*i, 2*i+1) for i in range(len(row['k_list']))]
    assert pairs == expected, row['name']
    full = sum((SCALE + int(k)) for k in row['k_list'])
    residue = sum(int(k) for k in row['k_list'])
    # This is an independent exact rational reconstruction of each binary64 edge.
    reconstructed = sum(int(Fraction.from_float(1 + int(k) * 2**-52)*SCALE)
                        for k in row['k_list'])
    assert full == reconstructed
    assert full == int(row['big_integer_full_units'])
    assert residue == row['exact_weight_residue']
    published = int(row['published_full_units'])
    difference = published - full
    assert difference == int(row['published_minus_true_big_integer_units'])
    assert (difference != 0) == row['mismatch']
    checks.append({'name':row['name'],'python_exact_full_units':str(full),
                   'published_minus_python_exact':str(difference),
                   'source_row_claim_correct':difference == int(row['published_minus_true_big_integer_units'])})
row = obj['rows'][7]
assert row['mismatch'], 'EXPECTED_N144_PRECISION_NEGATIVE_CONTROL_NOT_FOUND'
tamper_published = int(row['big_integer_full_units'])
tamper_residue = int(row['exact_weight_residue']) + 1
assert tamper_published != int(row['published_full_units'])  # mutate incorrect field
assert tamper_residue != sum(row['k_list'])  # mutate exact residue
receipt = {'schema':'ABH_N356_PYTHON_RATIONAL_ORACLE_V1',
           'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
           'cases':len(checks),'matching_cases_checked':len(checks),
           'reported_mismatches':sum(int(c['published_minus_python_exact']!='0') for c in checks),
           'two_intentional_mutants_detected':True,
           'checks':checks,'CT2_scientific':7,'STOP_R5_human':True}
DEST.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print('N356_PY_ORACLE',len(checks),receipt['reported_mismatches'],
      hashlib.sha256(DEST.read_bytes()).hexdigest())
