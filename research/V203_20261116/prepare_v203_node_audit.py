"""Export all registered native checkpoints for an independent JS evaluator."""
from pathlib import Path
import hashlib
import json
import numpy as np

B=Path(__file__).resolve().parent
F=B/'results/V203_EXACT_GRADIENT_FLOWS'
rows=json.loads((F/'SUMMARY.json').read_text(encoding='utf-8'))['rows']
records=[]
for row in rows:
    stem=f"{row['kind']}_{row['seed']}_{'NPG' if row['natural'] else 'EPG'}"
    data=np.load(F/f'{stem}.npz')
    for snap in row['snapshots']:
        ix=int(np.flatnonzero(data['times']==snap['time'])[0])
        records.append(dict(case=stem,time=snap['time'],logits=data['logits'][ix].tolist(),
            expected=snap,check_best_response=snap['time']==6000))
    if 'precision_run' in row:
        data=np.load(F/f'{stem}_PRECISION.npz')
        records.append(dict(case=stem+'_PRECISION',time=6000,logits=data['logits'][-1].tolist(),
            expected=row['precision_run']['snapshots'][-1],check_best_response=True))
payload=B/'results/V203_NODE_INPUT.json'
assert not payload.exists()
payload.write_text(json.dumps(dict(losses=[1,1,7,7],records=records)),encoding='utf-8')
original=B/'validation_node/v202_independent_audit.cjs'
assert hashlib.sha256(original.read_bytes()).hexdigest()=='e3130a034e71e072102c0bf74c333475d4d7ec54199dc6a58e1eef255118c65b'
source=original.read_text(encoding='utf-8')
functions=source[source.index('const stock='):source.index("const arms=")]
runner="""/* Independent-language literal-enumeration audit, post hoc.
   Reuses the previously audited JS physics; never calls Python operators. */
const fs=require('fs'),path=require('path');
const base=path.resolve(__dirname,'..');
const output=path.join(base,'results','V203_NODE_INDEPENDENT_AUDIT.json');
if(fs.existsSync(output))throw Error('Preserve earlier output');
"""+functions+"""
const input=JSON.parse(fs.readFileSync(path.join(base,'results','V203_NODE_INPUT.json'),'utf8'));
let maxNativeError=0,maxBehaviorError=0,maxBRerror=0,cases=0,brChecks=0;
const checked=[];
for(const rec of input.records){
 const p=rec.logits.map(player=>player.flatMap(h=>h.map(heads=>heads.map(v=>1/(1+Math.exp(-Math.max(-12,Math.min(12,v))))))));
 const own=evaluate(p,input.losses,true), e=rec.expected.native_evaluation;
 let error=Math.max(Math.abs(own.good-e.discounted_GOOD_joint_rate),Math.abs(own.disabled-e.disabled_payment_GOOD_rate));
 for(let i=0;i<4;i++)error=Math.max(error,Math.abs(own.returns[i]-e.normalized_private_return[i]));
 const functional=Math.min(...own.returns.map(x=>x-aut))>=.02&&own.good>=.20&&own.good-own.disabled>=.10;
 if(error>1e-9||functional!==e.functional)throw Error('Native mismatch '+rec.case+'/'+rec.time+'/'+error);
 maxNativeError=Math.max(maxNativeError,error);
 const eps=.20-.18*Math.min(rec.time/48,1);
 const mixed=p.map(player=>player.map(heads=>heads.map(v=>eps/2+(1-eps)*v)));
 const behavior=evaluate(mixed,input.losses,true);
 for(let i=0;i<4;i++)maxBehaviorError=Math.max(maxBehaviorError,Math.abs(behavior.returns[i]-rec.expected.behavior_normalized_private_return[i]));
 if(maxBehaviorError>1e-9)throw Error('Behavior value mismatch');
 if(rec.check_best_response)for(let i=0;i<4;i++){
  const br=bestResponse(p,input.losses,i);
  const err=Math.abs(.05*br.value-own.returns[i]-rec.expected.public_deviations.normalized_gain_per_agent[i]);
  if(err>1e-8)throw Error('BR mismatch '+rec.case+'/'+i+'/'+err);
  maxBRerror=Math.max(maxBRerror,err);brChecks++;
 }
 cases++;checked.push({case:rec.case,time:rec.time,error,functional});
}
const result={status:'PASS',cases,scalar_native_checks:6*cases,scalar_behavior_checks:4*cases,
 public_best_response_checks:brChecks,maxNativeError,maxBehaviorError,maxBRerror,
 method:'Independent JavaScript literal enumeration and value iteration; native sigmoid independently reconstructed from logits',
 external_scientific_confirmation:false,checked};
fs.writeFileSync(output,JSON.stringify(result,null,2));
process.stdout.write(JSON.stringify({...result,checked:undefined})+'\\n');
"""
target=B/'validation_node/v203_independent_audit.cjs'
assert not target.exists()
target.write_text(runner,encoding='utf-8')
print(json.dumps(dict(checkpoints=len(records),node_source=str(target))))
