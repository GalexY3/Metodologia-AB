"""Independent Python check for matching results and timeout evidence in N358."""
import hashlib,json
from fractions import Fraction
from pathlib import Path
root=Path(__file__).resolve().parent.parent
src=root/'outcomes'/'N358_HARD_WALL_RESULTS.json'
dest=root/'outcomes'/'N358_INDEPENDENT_AUDIT.json'
assert not dest.exists()
x=json.loads(src.read_text('utf8'))
assert x['schema']=='ABH_N358_EXTERNAL_HARD_WALL_PROSPECTIVE_V1'
assert len(x['cases'])==8
names={c['name'] for c in x['cases']}
assert len(names)==8
rows=[]
for case in x['cases']:
 assert case['status']==case['expectedStatus']
 if case['status']=='PASS':
  m=case['matching']
  pairs={tuple(sorted(edge)) for edge in m['pairs']}
  # The worker emits graph edges as {pair:[a,b],weight:w}, not 3-tuples.
  graph={(min(*e['pair']),max(*e['pair'])):Fraction.from_float(e['weight'])
         for e in case['edges']}
  assert len(pairs)==m['cardinality']
  assert len({v for p in pairs for v in p})==len(pairs)*2
  expected=sum(int(graph[p]*(2**52)) for p in pairs)
  assert str(expected)==m['full_units_decimal']
  assert m['certificate']['certified']
  rows.append({'name':case['name'],'exact_fraction_objective':str(expected),
               'matching_certified':True})
 else:
  assert case['certified'] is False
  if case['status']=='RESOURCE_HARD_WALL':
   assert case['elapsed_ms']<1750
   assert case['elapsed_ms']>0
assert len(rows)==3
assert sum(c['status']=='RESOURCE_HARD_WALL' for c in x['cases'])==2
assert {c['status'] for c in x['cases'] if c['status']!='PASS'}=={
 'RESOURCE_HARD_WALL','INVALID_WORKER_JSON','WORKER_FAILURE','RESOURCE_OUTPUT'}
o={'schema':'ABH_N358_INDEPENDENT_PYTHON_AUDIT_V1',
   'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
   'passed':8,'expected':8,'three_independent_exact_objectives':rows,
   'two_external_hard_timeouts':2,'three_fail_closed_worker_outputs':3,
   'scientific_CT2':7,'STOP_R5_human':True}
dest.write_text(json.dumps(o,indent=2)+'\n',encoding='utf8')
print('N358_PY_AUDIT',o['passed'],
 hashlib.sha256(dest.read_bytes()).hexdigest())
