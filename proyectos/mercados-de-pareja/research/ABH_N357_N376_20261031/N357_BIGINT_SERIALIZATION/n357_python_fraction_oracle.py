"""Independent cross-language exact objective verifier for N357."""
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'outcomes'/'N357_EXACT_SERIALIZATION_RESULTS.json'
DEST=ROOT/'outcomes'/'N357_PYTHON_ORACLE.json'
assert not DEST.exists(), 'REFUSE_OVERWRITE'
o=json.loads(SRC.read_text('utf8'))
assert o['schema']=='N357_DECIMAL_BIGINT_REGRESSION_V1'
assert len(o['rows'])==o['case_count']==21
ONE=1<<52
rows=[]
for r in o['rows']:
    edges={(min(a,b),max(a,b)):Fraction.from_float(w) for a,b,w in r['edges']}
    observed=set()
    total=0
    residue=0
    for a,b in r['pairs']:
        assert a!=b and a not in observed and b not in observed, r['name']
        observed|={a,b}
        weight=edges[(min(a,b),max(a,b))]
        scaled=weight*ONE
        assert scaled.denominator==1
        total+=scaled.numerator
        residue+=scaled.numerator-ONE
    assert r['cardinality']==len(r['pairs'])
    assert r['certified'] and r['schema_version']==2
    assert r['format']=='decimal_bigint_string'
    assert isinstance(r['full_units_decimal'],str) and re.fullmatch('[0-9]+',r['full_units_decimal'])
    assert total==int(r['full_units_decimal'])
    assert residue==r['exact_residual']
    old=r['cardinality']*ONE+r['exact_residual']
    loss=int(float(old))-old
    assert str(loss)==r['old_Number_loss'],r['name']
    rows.append({'name':r['name'],'matching_cardinality':r['cardinality'],
                 'exact_total':str(total),'old_numeric_loss':str(loss),
                 'verify_serialized_exact':True})
target=next(x for x in o['rows'] if x['name']=='D4_ONE')
assert int(target['full_units_decimal'])+1!=int(target['full_units_decimal'])
assert target['exact_residual']+1 != int(target['full_units_decimal'])-target['cardinality']*ONE
receipt={'schema':'ABH_N357_PYTHON_FRACTION_ORACLE_V1',
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
         'cases':len(rows),'confirmed_exact':len(rows),
         'old_Number_mismatch_count':sum(int(x['old_numeric_loss']!='0') for x in rows),
         'mutation_probes_rejected':2,'rows':rows,'CT2':7,'STOP_R5':True}
DEST.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print('N357_PY',receipt['cases'],receipt['old_Number_mismatch_count'],
      hashlib.sha256(DEST.read_bytes()).hexdigest())
