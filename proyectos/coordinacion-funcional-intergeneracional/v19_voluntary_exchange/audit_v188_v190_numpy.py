"""Independent NumPy evaluation of saved PyTorch weights; no training.

Does not call the simulator/model/evaluation routines. Checks all final histories,
or an explicitly requested already-written V190 checkpoint during a running job.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import torch
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
P=31


def reference(model, policy, mask):
    """Enumerate all a,b and integrate all possible messages in float64."""
    w={k:v.detach().cpu().numpy().astype(np.float64) for k,v in model.items()}
    n=len(policy);aa,bb=np.indices((P,P));target=(aa+bb)%P
    rows=[]
    for s in range(n):
        # This NumPy operation is independent of BatchedReceiver.forward/bmm.
        hidden=w['message'][s,:,None,:]+w['context'][s,None,:,:]
        logits=np.einsum('mbh,hy->mby',hidden**2,w['output'][s])
        prediction=logits.argmax(-1)
        mapping=policy[s].argmax(-1)
        greedy=(prediction[mapping,:]==target)
        expected=np.sum(policy[s,:,:,None]*(prediction[None,:,:]==target[:,None,:]),axis=1)
        train=mask[s]
        # Posthoc diagnostics. These are conditional on the existing receiver
        # and the greedy code, not a Nash claim over all neural policies.
        train_cells=np.zeros((P,P),dtype=np.int64)
        for a in range(P):train_cells[mapping[a]]+=train[a]
        oracle_correct=int((train_cells>0).sum())
        actual_correct=int(greedy[train].sum())
        alternative_correct=((prediction[None,:,:]==target[:,None,:])*train[:,None,:]).sum(-1)
        current_correct=alternative_correct[np.arange(P),mapping]
        best_improvement=int((alternative_correct.max(1)-current_correct).max())
        rows.append(dict(train=float(greedy[train].mean()),test=float(greedy[~train].mean()),
                         train_expected=float(expected[train].mean()),test_expected=float(expected[~train].mean()),
                         symbols=int(np.unique(mapping).size),
                         capacity=float(policy[s].max(0).sum()/P),
                         training_oracle_given_greedy_code=oracle_correct/int(train.sum()),
                         receiver_attains_greedy_training_ceiling=actual_correct==oracle_correct,
                         residual_receiver_training_errors=oracle_correct-actual_correct,
                         maximum_train_cases_gained_by_one_state_message_change=best_improvement,
                         sender_has_improving_greedy_deviation=best_improvement>0,
                         interpretation='posthoc, fixed existing receiver and greedy sender only; not global Nash equilibrium'))
    return rows


def softmax(x):
    x=x.detach().cpu().numpy().astype(np.float64)
    x=np.exp(x-x.max(-1,keepdims=True))
    return x/x.sum(-1,keepdims=True)


def checkpoint_audit(path, experiment, support, family, step):
    d=torch.load(path,map_location='cpu',weights_only=False)
    assert d['step']==step
    seeds=list(range(188115,188123)) if experiment==188 else list(range(190115,190123))
    if family=='FIXED_PROTOCOL':
        policy=np.eye(P)[np.stack([np.random.default_rng(seed+20000).permutation(P) for seed in seeds])]
    elif family in ['REINFORCE','PRIVATE']:policy=softmax(d['actor'])
    else:
        counts=d['counts'].astype(np.float64)
        totals=counts.sum(-1,keepdims=True)
        policy=np.divide(counts,totals,out=np.full_like(counts,1/P),where=totals>0)
    if experiment==188:
        # Reconstruct V185's frozen unordered-pair partition independently.
        pairs=np.array([(a,b) for a in range(P) for b in range(a,P)])
        rng=np.random.default_rng(185000)
        order=rng.permutation(len(pairs));mask=np.zeros((P,P),dtype=bool)
        for a,b in pairs[order[:int(.4*len(pairs))]]:mask[a,b]=mask[b,a]=True
        assert mask.sum()==387
        masks=np.stack([mask]*8)
    else:
        masks=np.stack([np.load(B/f'results/V189B_MATCHED_CONTEXTS/pair_{i//2}.npz')[support.lower()] for i in range(8)])
    rows=reference(d['model'],policy,masks)
    checks=[]
    for s in range(8):
        saved=d['histories'][s][-1]
        for field in ['train','test','train_expected','test_expected']:
            error=abs(rows[s][field]-saved[field])
            checks.append(dict(experiment=experiment,support=support,family=family,seed=seeds[s],step=step,
                               field=field,reference=rows[s][field],saved=saved[field],
                               error=error,tolerance=2e-6,passed=bool(error<=2e-6)))
        symbol_key='protocol_symbols' if experiment==188 else 'symbols'
        assert rows[s]['symbols']==saved[symbol_key]
        weighted=np.mean([rows[s]['train_expected']]*int(masks[s].sum())+
                         [rows[s]['test_expected']]*(P*P-int(masks[s].sum())))
        assert weighted<=rows[s]['capacity']+2e-6
    return dict(checkpoint=path.relative_to(B).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                checks=checks,reference_rows=rows,capacities_and_symbols_passed=True)


def main(interim):
    audits=[]
    if interim:
        support,family,step='LOW','FIXED_PROTOCOL',30000
        path=B/f'results/V190_LOSSY_MEMORIZATION/{support}_{family}/checkpoint_{step}.pt'
        audits.append(checkpoint_audit(path,190,support,family,step))
        output=B/'results/V190_NUMPY_INTERIM_AUDIT.json'
    else:
        assert (B/'results/V190_LOSSY_MEMORIZATION/SUMMARY.json').exists()
        for family in ['FIXED_PROTOCOL','REINFORCE','URN_PURE','URN_LIMITED']:
            audits.append(checkpoint_audit(B/f'results/V188_PRIVATE_CONVENTIONS/{family}/checkpoint_30000.pt',188,None,family,30000))
        for support in ['LOW','HIGH']:
            for family in ['FIXED_PROTOCOL','PRIVATE']:
                audits.append(checkpoint_audit(B/f'results/V190_LOSSY_MEMORIZATION/{support}_{family}/checkpoint_60000.pt',190,support,family,60000))
        output=B/'results/V188_V190_NUMPY_FINAL_AUDIT.json'
    failures=[c for a in audits for c in a['checks'] if not c['passed']]
    summary=dict(independent_numpy_forward=True,no_new_training=True,audits=audits,failures=failures,
                 numeric_checks=sum(len(a['checks']) for a in audits),
                 max_error=max(c['error'] for a in audits for c in a['checks']))
    assert not output.exists()
    output.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    assert not failures,failures
    print(json.dumps({k:v for k,v in summary.items() if k!='audits'}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--interim',action='store_true');args=parser.parse_args()
    print('LIMITS',apply_limits(2));torch.set_num_threads(2);main(args.interim)
