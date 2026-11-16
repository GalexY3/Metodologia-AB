"""Post hoc export of every valid native checkpoint; no new learning."""
from pathlib import Path
import hashlib
import json
import numpy as np

B=Path(__file__).resolve().parent
F=B/'results/V204_LOLA_NET_RETURN'
rows=json.loads((F/'SUMMARY.json').read_text(encoding='utf-8'))['rows']
records=[];missing=[]
for row in rows:
    stem=f"{row['kind']}_{row['seed']}_LOLA"
    if row['status']!='SUCCESS':missing.append(stem);continue
    data=np.load(F/f'{stem}.npz')
    for snap in row['snapshots']:
        ix=int(np.flatnonzero(data['times']==snap['time'])[0])
        records.append(dict(case=stem,time=snap['time'],logits=data['logits'][ix].tolist(),
            expected=snap,check_best_response=snap['time']==6000))
    if row.get('precision_run',{}).get('status')=='SUCCESS':
        data=np.load(F/f'{stem}_PRECISION.npz')
        records.append(dict(case=stem+'_PRECISION',time=6000,logits=data['logits'][-1].tolist(),
            expected=row['precision_run']['snapshots'][-1],check_best_response=True))
out=B/'results/V204_NODE_INPUT.json';assert not out.exists()
out.write_text(json.dumps(dict(losses=[1,1,7,7],records=records,missing=missing)),encoding='utf-8')
source=B/'validation_node/v203_independent_audit.cjs'
code=source.read_text(encoding='utf-8').replace('V203_NODE_INPUT','V204_NODE_INPUT').replace('V203_NODE_INDEPENDENT_AUDIT','V204_NODE_INDEPENDENT_AUDIT')
target=B/'validation_node/v204_independent_audit.cjs';assert not target.exists()
target.write_text(code,encoding='utf-8')
print(json.dumps(dict(valid_checkpoints=len(records),missing_cases=missing,source_JS_sha256=hashlib.sha256(source.read_bytes()).hexdigest())))
