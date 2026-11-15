"""Freeze each neural peer at its first training-selected memorization point.

The active peer's local generalization is the estimand. Joint test accuracy can
be bounded by an unlearned frozen peer and is not evidence of causal necessity.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from pathlib import Path
import argparse
import copy
import hashlib
import json
import time
import numpy as np
import torch
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver,extract_optimizer
from v191_dual_neural_credit import P,N,SEEDS,sample_action,full_loss,environment_feedback
from v192_dual_neural_learning import evaluate

BASE=Path(__file__).resolve().parent
PARENT=BASE/'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL'
OUT=BASE/'results/V193_FROZEN_PEER'
END=60000


def data_for(seeds):
    sources=[np.load(BASE/f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz') for seed in seeds]
    arrays={k:np.stack([d[k] for d in sources]) for k in ['a','b','f','masks']}
    tensors={k:torch.tensor(arrays[k],device='cuda',dtype=torch.long) for k in ['a','b','f']}
    return arrays,tensors


def initial(seed):
    return torch.load(PARENT/f'first_memorization_s{seed}.pt',map_location='cpu',weights_only=False)


def merge_optimizer(states):
    merged=copy.deepcopy(states[0])
    for other in states[1:]:assert other['param_groups']==states[0]['param_groups']
    for pid,values in merged['state'].items():
        for key,value in list(values.items()):
            parts=[state['state'][pid][key] for state in states]
            if isinstance(value,torch.Tensor) and value.ndim:
                values[key]=torch.cat([part.detach().cpu() for part in parts],dim=0)
            elif isinstance(value,torch.Tensor):
                reference=value.detach().cpu()
                assert all(torch.equal(part.detach().cpu(),reference) for part in parts),'Mismatched active optimizer clocks'
                values[key]=reference.clone()
            else:assert all(part==value for part in parts)
    return merged


def load_group(bundles,seeds,active):
    models=[BatchedReceiver([2*seed+role for seed in seeds],device='cuda') for role in range(2)]
    optimizers=[]
    for role in range(2):
        keys=bundles[0]['models'][role].keys()
        model_state={k:torch.cat([b['models'][role][k] for b in bundles],0) for k in keys}
        models[role].load_state_dict(model_state);models[role].requires_grad_(active[role])
        if active[role]:
            optimizer=torch.optim.AdamW(models[role].parameters(),lr=.001,weight_decay=1.,betas=(.9,.98))
            optimizer.load_state_dict(merge_optimizer([b['optimizers'][role] for b in bundles]))
        else:optimizer=None
        optimizers.append(optimizer)
    rngs=[]
    for b in bundles:
        rng=np.random.default_rng(0);rng.bit_generator.state=copy.deepcopy(b['rng_state']);rngs.append(rng)
    return models,optimizers,rngs


def update(models,optimizers,rngs,tensors,active):
    coins=torch.tensor(np.stack([r.random((2,N)) for r in rngs]),device='cuda')
    permutation=torch.tensor(np.stack([r.permutation(N) for r in rngs]),device='cuda')
    a,b,f=[tensors[k] for k in ['a','b','f']]
    values=[models[role](a[:,role],b[:,role]) for role in range(2)]
    actions=[sample_action(values[role].detach().argmax(2),coins[:,role]) for role in range(2)]
    pa,pb,_,_=environment_feedback(f[:,0],f[:,1],actions[0],actions[1],permutation)
    losses=[full_loss(values[0],pa),full_loss(values[1],pb)]
    for role in range(2):
        if active[role]:
            optimizers[role].zero_grad(set_to_none=True);losses[role].backward();optimizers[role].step()


def export_one(models,optimizers,rngs,s,step,seed):
    return dict(seed=seed,step=step,
                models=[{k:v[s:s+1].detach().cpu().clone() for k,v in m.state_dict().items()} for m in models],
                optimizers=[extract_optimizer(opt,s) if opt is not None else None for opt in optimizers],
                rng_state=copy.deepcopy(rngs[s].bit_generator.state))


def prepare_common(frozen_role=None):
    """Align active clocks, retaining each frozen peer's original cut.

    Padding uses four identical technical copies to keep the original batch4
    CUDA kernels. In scientific arms the padding is part of the intervention,
    so it is executed only after preregistration, never in technical().
    """
    parents=[initial(seed) for seed in SEEDS];common=max(b['step'] for b in parents)
    active=[role!=frozen_role for role in range(2)]
    bundles=[]
    for seed,parent in zip(SEEDS,parents):
        bundle=copy.deepcopy(parent)
        if parent['step']<common:
            copies=[copy.deepcopy(parent) for _ in range(4)]
            models,opts,rngs=load_group(copies,[seed]*4,active)
            _,tensors=data_for([seed]*4)
            for _ in range(parent['step'],common):update(models,opts,rngs,tensors,active)
            bundle=export_one(models,opts,rngs,0,common,seed)
            del models,opts;torch.cuda.empty_cache()
        bundles.append(bundle)
    return bundles,common,active,[b['step'] for b in parents]


def compare_tensors(expected,actual,path='',rows=None):
    if rows is None:rows=[]
    if isinstance(expected,torch.Tensor):
        value=actual.detach().cpu();reference=expected.detach().cpu()
        assert reference.shape==value.shape,path
        error=float((reference-value).abs().max()) if reference.numel() else 0.
        rows.append(dict(path=path,bit_identical=bool(torch.equal(reference,value)),max_error=error))
    elif isinstance(expected,dict):
        assert expected.keys()==actual.keys(),path
        for key in expected:compare_tensors(expected[key],actual[key],path+'/'+str(key),rows)
    elif isinstance(expected,(list,tuple)):
        assert len(expected)==len(actual),path
        for i,(a,b) in enumerate(zip(expected,actual)):compare_tensors(a,b,path+'/'+str(i),rows)
    else:assert expected==actual,path
    return rows


def technical():
    assert not OUT.exists()
    bundles,start,active,cuts=prepare_common(None)
    models,opts,rngs=load_group(bundles,SEEDS,active);_,tensors=data_for(SEEDS)
    block=time.monotonic()
    for step in range(start+1,5001):
        update(models,opts,rngs,tensors,active)
        if step%100==0:
            time.sleep(max(0.,.4-(time.monotonic()-block)));block=time.monotonic()
    expected=torch.load(PARENT/'checkpoint_5000.pt',map_location='cpu',weights_only=False)
    comparisons=compare_tensors(expected['models'],[m.state_dict() for m in models],'/models')
    compare_tensors(expected['optimizers'],[o.state_dict() for o in opts],'/optimizers',comparisons)
    assert expected['rng_states']==[r.bit_generator.state for r in rngs]
    result=dict(historical_replay_only=True,new_scientific_training=False,original_cuts=cuts,
                aligned_step=start,comparison_step=5000,comparisons=comparisons,
                all_tensors_bit_identical=all(r['bit_identical'] for r in comparisons),
                maximum_error=max(r['max_error'] for r in comparisons),RNG_states_identical=True,
                original_checkpoint_sha256=hashlib.sha256((PARENT/'checkpoint_5000.pt').read_bytes()).hexdigest())
    path=BASE/'results/V193_TECHNICAL_REPLAY.json';assert not path.exists()
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert result['all_tensors_bit_identical'],result
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'}),flush=True)


def train_arm(frozen_role):
    name='FREEZE_'+('A' if frozen_role==0 else 'B');folder=OUT/name;folder.mkdir(exist_ok=False)
    bundles,start,active,cuts=prepare_common(frozen_role)
    models,opts,rngs=load_group(bundles,SEEDS,active);arrays,tensors=data_for(SEEDS)
    frozen_before={k:v.detach().clone() for k,v in models[frozen_role].state_dict().items()}
    torch.save(dict(bundles=bundles,common_step=start,individual_freeze_steps=cuts),folder/'initial_aligned_state.pt')
    histories=[[] for _ in SEEDS];streak=[0]*len(SEEDS);t_gen=[None]*len(SEEDS)
    active_role=1-frozen_role;field='test_'+('A' if active_role==0 else 'B')
    block=time.monotonic();started=block;checkpoint_parity=[]
    for step in range(start+1,END+1):
        update(models,opts,rngs,tensors,active)
        if step%100==0:
            rows=evaluate(models,arrays,'cuda')
            for s,row in enumerate(rows):
                row['step']=step
                h=row['test_error_histograms'][frozen_role]
                row['joint_test_upper_bound_from_frozen_peer']=float(max(h))
                assert row['test_joint_greedy']<=row['joint_test_upper_bound_from_frozen_peer']+1e-12
                histories[s].append(row)
                streak[s]=streak[s]+1 if row[field]>=.95 else 0
                if t_gen[s] is None and streak[s]>=5:t_gen[s]=step
            if step%1000==0:print('V193',name,step,'active_test',round(np.mean([r[field] for r in rows]),4),
                                  'joint_test',round(np.mean([r['test_joint_greedy'] for r in rows]),4),
                                  'sec',round(time.monotonic()-started,1),flush=True)
            if step%5000==0:
                assert all(torch.equal(v,frozen_before[k]) for k,v in models[frozen_role].state_dict().items())
                source=torch.load(PARENT/f'checkpoint_{step}.pt',map_location='cpu',weights_only=False)
                comparisons=compare_tensors(source['models'][active_role],models[active_role].state_dict())
                optimizer_comparisons=compare_tensors(source['optimizers'][active_role],opts[active_role].state_dict())
                checkpoint_parity.append(dict(step=step,model_all_bits_equal=all(c['bit_identical'] for c in comparisons),
                    optimizer_all_bits_equal=all(c['bit_identical'] for c in optimizer_comparisons),
                    model_max_error=max(c['max_error'] for c in comparisons),
                    RNG_states_identical=source['rng_states']==[r.bit_generator.state for r in rngs]))
                torch.save(dict(models=[m.state_dict() for m in models],active_optimizer=opts[active_role].state_dict(),
                                step=step,rng_states=[r.bit_generator.state for r in rngs],histories=histories),folder/f'checkpoint_{step}.pt')
                (folder/'progress.json').write_text(json.dumps(dict(step=step,rows=rows),indent=2),encoding='utf-8')
            time.sleep(max(0.,.4-(time.monotonic()-block)));block=time.monotonic()
    results=[]
    for s,seed in enumerate(SEEDS):
        r=dict(seed=seed,arm=name,frozen_role=frozen_role,active_role=active_role,freeze_step=cuts[s],
               final=histories[s][-1],history=histories[s],t_gen_active=t_gen[s],
               active_local_generalization_passed=histories[s][-1][field]>=.95)
        (folder/f'metrics_s{seed}.json').write_text(json.dumps(r,indent=2),encoding='utf-8');results.append(r)
    (folder/'CHECKPOINT_PARITY_WITH_JOINT.json').write_text(json.dumps(checkpoint_parity,indent=2),encoding='utf-8')
    del models,opts;torch.cuda.empty_cache()
    return results


def run():
    receipt=json.loads((BASE/'results/V193_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path,sha in receipt['source_sha256'].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==sha,path
    assert json.loads((BASE/'results/V193_TECHNICAL_REPLAY.json').read_text())['all_tensors_bit_identical']
    OUT.mkdir(exist_ok=False)
    (OUT/'MANIFEST.json').write_text(json.dumps(dict(preregistration=receipt,parent_histories=4,
        counterfactual_continuations=8,independent_new_training_roots=0,
        common_interests_and_counterfactual_feedback_imposed=True),indent=2),encoding='utf-8')
    results=[]
    for role in [0,1]:results.extend(train_arm(role))
    counts={arm:sum(r['active_local_generalization_passed'] for r in results if r['arm']==arm) for arm in ['FREEZE_A','FREEZE_B']}
    deficits={arm:float(np.median([1-r['final']['test_'+('A' if r['active_role']==0 else 'B')] for r in results if r['arm']==arm])) for arm in counts}
    passed=all(counts[a]>=3 and deficits[a]<=.02 for a in counts)
    summary=dict(runs=[{k:v for k,v in r.items() if k!='history'} for r in results],active_local_pass_counts=counts,
                 median_active_deficits_against_joint=deficits,ongoing_coadaptation_necessity_refuted=bool(passed),
                 direct_test_of_formation_before_memorization=False,intrinsically_collective_grokking_accredited=False,
                 CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V193_COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='runs'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['technical','run']);a=p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False
    torch.cuda.set_per_process_memory_fraction(.35)
    {'technical':technical,'run':run}[a.command]()
