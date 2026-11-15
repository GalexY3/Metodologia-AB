"""Independent NumPy forward pass and explicit Cartesian game evaluation."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import torch
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
P=31;EPS=.1;SEEDS=list(range(192115,192119))


def audit(family,step,checkpoint_path=None):
    path=checkpoint_path or B/f'results/V192_DUAL_NEURAL_LEARNING/{family}/checkpoint_{step}.pt'
    checkpoint=torch.load(path,map_location='cpu',weights_only=False)
    assert checkpoint['step']==step
    aa,bb=np.indices((P,P));truth=(aa+bb)%P
    checks=[];diagnostics=[]
    for s,seed in enumerate(SEEDS):
        masks=np.load(B/f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz')['masks']
        predictions=[];margins=[]
        for role in range(2):
            weights={k:v[s].numpy().astype(np.float64) for k,v in checkpoint['models'][role].items()}
            hidden=weights['message'][:,None,:]+weights['context'][None,:,:]
            values=np.einsum('abh,hp->abp',hidden**2,weights['output'])
            predictions.append(values.argmax(2))
            top2=np.partition(values,-2,axis=2)[:,:,-2:]
            margins.append(float((top2[:,:,1]-top2[:,:,0]).min()))
        rows={}
        # Independent explicit enumeration of every pair of local inputs,
        # not reuse of the simulator's error-histogram dot product.
        for key,parts in [('train',masks),('test',~masks)]:
            chosen=[predictions[r][parts[r]] for r in range(2)]
            local_truth=[truth[parts[r]] for r in range(2)]
            actual=(chosen[0][:,None]+chosen[1][None,:])%P
            target=(local_truth[0][:,None]+local_truth[1][None,:])%P
            acc=float((actual==target).mean());rows[key+'_joint_greedy']=acc
            rows[key+'_joint_behavior_expected']=(1-EPS)**2*acc+(1-(1-EPS)**2)/P
        train_error=(predictions[0]-truth)%P
        gauge=int(np.bincount(train_error[masks[0]],minlength=P).argmax())
        for role,offset in [(0,gauge),(1,(-gauge)%P)]:
            correct=(predictions[role]-truth)%P==offset
            label='A' if role==0 else 'B'
            rows['train_'+label]=float(correct[masks[role]].mean())
            rows['test_'+label]=float(correct[~masks[role]].mean())
        saved=checkpoint['histories'][s][-1]
        for field,value in rows.items():
            error=abs(value-saved[field])
            checks.append(dict(family=family,seed=seed,step=step,field=field,reference=value,saved=saved[field],
                               error=error,tolerance=1e-7,passed=bool(error<=1e-7)))
        diagnostics.append(dict(seed=seed,minimum_output_action_margins=margins,
                                Cartesian_train_pairs=384**2,Cartesian_test_pairs=577**2))
    return dict(family=family,step=step,checkpoint_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),checks=checks,diagnostics=diagnostics)


def main(interim):
    if interim:
        audits=[audit('ORACLE_FULL',20000)];out=B/'results/V192_NUMPY_INTERIM_AUDIT.json'
    else:
        summary=json.loads((B/'results/V192_DUAL_NEURAL_LEARNING/SUMMARY.json').read_text(encoding='utf-8'))
        families=sorted({r['family'] for r in summary['runs']})
        audits=[audit(family,60000) for family in families];out=B/'results/V192_NUMPY_FINAL_AUDIT.json'
    failures=[c for a in audits for c in a['checks'] if not c['passed']]
    result=dict(audits=audits,failures=failures,checks=sum(len(a['checks']) for a in audits),
                max_error=max(c['error'] for a in audits for c in a['checks']),
                independent_numpy_forward=True,explicit_cartesian_pair_enumeration=True,new_training_executed=False)
    assert not out.exists();out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert not failures,failures
    print(json.dumps({k:v for k,v in result.items() if k!='audits'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--interim',action='store_true');a=p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);main(a.interim)
