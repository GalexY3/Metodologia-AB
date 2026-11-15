"""Controlled support geometry; independent private sender/receiver learning.

The environment permits a lossy perfect-fit convention but never provides one
to PRIVATE. Known information bounds are implementation checks, not discoveries.
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
from torch import nn
from numba import njit
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver,extract_optimizer
from v187_classical_signaling import choose

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V190_LOSSY_MEMORIZATION'
P=31;STEPS=60000;SEEDS=list(range(190115,190123))


@njit(cache=True)
def sample(policies,a,coins):
    result=np.zeros(a.shape,dtype=np.int64)
    for s in range(len(policies)):
        for i in range(a.shape[1]):result[s,i]=choose(policies[s,a[s,i]],coins[s,i])
    return result


def data_for(support):
    masks=[];aa=[];bb=[];yy=[]
    for pair in range(4):
        d=np.load(BASE/f'results/V189B_MATCHED_CONTEXTS/pair_{pair}.npz')
        mask=d['low' if support=='LOW' else 'high']
        assert mask.sum()==372
        for _ in range(2):
            masks.append(mask.copy());aa.append(d['a'][mask.ravel()]);bb.append(d['b'][mask.ravel()]);yy.append(d['y'][mask.ravel()])
    return np.stack(masks),np.stack(aa),np.stack(bb),np.stack(yy)


@torch.no_grad()
def evaluate(model,policies,full,masks):
    a,b,y=full;n=len(policies);device=policies.device
    protocols=policies.argmax(2)
    logits=model(protocols[:,a],b[None].expand(n,-1));correct=logits.argmax(2)==y[None]
    all_m,all_b=np.indices((P,P))
    mm=torch.tensor(all_m.ravel(),device=device)[None].expand(n,-1)
    cb=torch.tensor(all_b.ravel(),device=device)[None].expand(n,-1)
    predictions=model(mm,cb).argmax(2).reshape(n,P,P)
    targets=(torch.arange(P,device=device)[:,None]+torch.arange(P,device=device)[None,:])%P
    probabilities=(policies[:,:,:,None]*(predictions[:,None,:,:]==targets[None,:,None,:]).float()).sum(2).reshape(n,-1)
    onehot=nn.functional.one_hot(protocols,P).float().transpose(1,2)
    test_counts=torch.bmm(onehot,torch.tensor((~masks).astype(float),device=device,dtype=torch.float32))
    rows=[]
    for s in range(n):
        train=torch.tensor(masks[s].ravel(),device=device)
        tr=float(correct[s,train].float().mean());te=float(correct[s,~train].float().mean())
        tr_e=float(probabilities[s,train].mean());te_e=float(probabilities[s,~train].mean())
        k=int(protocols[s].unique().numel());bound=float(policies[s].max(0).values.sum()/P)
        capacity_test=(P*P*bound-372*tr_e)/589
        assert te_e<=capacity_test+1e-5,(s,te_e,capacity_test)
        rows.append(dict(train=tr,test=te,train_expected=tr_e,test_expected=te_e,
                         train_nll=float(nn.functional.cross_entropy(logits[s,train],y[train])),
                         test_nll=float(nn.functional.cross_entropy(logits[s,~train],y[~train])),
                         symbols=k,entropy=float(-(policies[s]*policies[s].clamp_min(1e-12).log()).sum(1).mean()),
                         full_capacity_stochastic=bound,test_capacity_given_train_stochastic=capacity_test,
                         test_capacity_given_train_greedy=min(float((test_counts[s]>0).float().sum()/589),(k*P-372*tr)/589)))
    return rows


def technical():
    masks,a,b,y=data_for('LOW')
    assert a.shape==(8,372) and all(np.all(np.bincount(row,minlength=P)==12) for row in a)
    masks2,_,_,y2=data_for('HIGH')
    assert all(np.array_equal(np.bincount(y[s],minlength=P),np.bincount(y2[s],minlength=P)) for s in range(8))
    rng=np.random.default_rng(190900)
    probs=rng.random((8,P,P));probs/=probs.sum(2,keepdims=True)
    coins=rng.random(a.shape);got=sample(probs,a,coins)
    expected=np.array([[np.searchsorted(np.cumsum(probs[s,a[s,i]]),coins[s,i]*probs[s,a[s,i]].sum(),side='right')
                        for i in range(a.shape[1])] for s in range(8)])
    assert np.array_equal(got,expected)
    # Forward indices and likelihood gradients are already independently checked
    # in V188. Here check variable masks against individual explicit enumeration.
    model=BatchedReceiver(SEEDS,dtype=torch.float64)
    full_a,full_b=np.indices((P,P));full_y=(full_a+full_b)%P
    full=tuple(torch.tensor(v.ravel(),dtype=torch.long) for v in [full_a,full_b,full_y])
    policies=torch.tensor(probs,dtype=torch.float64)
    rows=evaluate(model,policies,full,masks)
    checks=[]
    with torch.no_grad():
        prediction=model(policies.argmax(2)[:,full[0]],full[1][None].expand(8,-1)).argmax(2).numpy()
        for s in range(8):
            mask=masks[s].ravel()
            for key,selected in [('train',mask),('test',~mask)]:
                error=abs(rows[s][key]-np.mean(prediction[s,selected]==full_y.ravel()[selected]))
                checks.append(dict(history=s,field=key,error=float(error),tolerance=1e-6,passed=bool(error<=1e-6)))
    result=dict(checks=checks,failures=[c for c in checks if not c['passed']],
                variable_private_input_sampler_matches_reference=True,
                input_and_output_marginals_verified=True,V188_independent_receiver_audit_reused=True,
                neural_training_executed=False)
    (BASE/'results/V190_TECHNICAL_AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert not result['failures'];print(json.dumps(result),flush=True)


def train(support,family):
    target=OUT/f'{support}_{family}';target.mkdir(exist_ok=False)
    masks,aa,bb,yy=data_for(support);n=len(SEEDS);device='cuda'
    a,b,y=(torch.tensor(v,dtype=torch.long,device=device) for v in [aa,bb,yy])
    flat_a,flat_b=np.indices((P,P));flat_y=(flat_a+flat_b)%P
    full=tuple(torch.tensor(v.ravel(),dtype=torch.long,device=device) for v in [flat_a,flat_b,flat_y])
    index=torch.arange(n,device=device)[:,None]
    model=BatchedReceiver(SEEDS,device=device)
    recopt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98))
    actor=nn.Parameter(torch.zeros((n,P,P),device=device));actopt=torch.optim.Adam([actor],lr=.03)
    baseline=torch.zeros((n,P),device=device)
    group_matrix=nn.functional.one_hot(a,P).float().transpose(1,2)/12.
    rngs=[np.random.default_rng(seed+10000) for seed in SEEDS]
    dictionary=None
    if family=='FIXED_PROTOCOL':dictionary=torch.tensor(np.stack([np.random.default_rng(seed+20000).permutation(P) for seed in SEEDS]),device=device)
    histories=[[] for _ in SEEDS];sm=[0]*n;sg=[0]*n;sl=[0]*n
    t_mem=[None]*n;t_gen=[None]*n;t_lossy=[None]*n
    start=time.monotonic();block=start
    for step in range(1,STEPS+1):
        coins=np.stack([r.random((372,3)) for r in rngs])
        log_probs=actor[index,a].log_softmax(2)
        policies=actor.softmax(2) if dictionary is None else nn.functional.one_hot(dictionary,P).float()
        messages_np=sample(policies.detach().cpu().double().numpy(),aa,coins[:,:,0])
        messages=torch.tensor(messages_np,device=device)
        logits=model(messages,b)
        reward=(logits.detach().argmax(2)==y).float()
        recopt.zero_grad(set_to_none=True)
        loss=nn.functional.cross_entropy(logits.reshape(-1,P),y.reshape(-1),reduction='none').reshape(n,-1).mean(1).sum()
        loss.backward();recopt.step()
        if family=='PRIVATE':
            advantage=(reward-baseline[index,a]).detach()
            entropy=-(log_probs.exp()*log_probs).sum(2).mean(1).sum()
            actor_loss=-(advantage*log_probs.gather(2,messages[:,:,None]).squeeze(2)).mean(1).sum()-.01*entropy
            actopt.zero_grad(set_to_none=True);actor_loss.backward();actopt.step()
        baseline=.95*baseline+.05*torch.bmm(group_matrix,reward[:,:,None]).squeeze(2).detach()
        if step%100==0:
            policies=actor.softmax(2) if dictionary is None else nn.functional.one_hot(dictionary,P).float()
            rows=evaluate(model,policies,full,masks)
            for s,row in enumerate(rows):
                row['step']=step;histories[s].append(row)
                sm[s]=sm[s]+1 if row['train']>=.99 else 0
                sg[s]=sg[s]+1 if row['test']>=.95 else 0
                sl[s]=sl[s]+1 if row['train']==1. and row['symbols']<31 else 0
                if t_mem[s] is None and sm[s]>=5:t_mem[s]=step
                if t_gen[s] is None and sg[s]>=5:t_gen[s]=step
                if t_lossy[s] is None and sl[s]>=5:
                    assert support=='LOW','HIGH graph forbids exact lossy memorization'
                    t_lossy[s]=step
                    snapshot=dict(seed=SEEDS[s],pair=s//2,support=support,family=family,step=step,
                                  model={k:v[s:s+1].detach().clone() for k,v in model.state_dict().items()},
                                  actor=actor[s:s+1].detach().clone(),baseline=baseline[s:s+1].detach().clone(),
                                  receiver_optimizer=extract_optimizer(recopt,s),actor_optimizer=extract_optimizer(actopt,s),
                                  rng_state=copy.deepcopy(rngs[s].bit_generator.state),history=copy.deepcopy(histories[s]),
                                  selection_uses_test=False)
                    torch.save(snapshot,target/f'first_lossy_memorization_s{SEEDS[s]}.pt')
            if step%1000==0:print('V190',support,family,step,'train',round(np.mean([r['train'] for r in rows]),4),
                                 'test',round(np.mean([r['test'] for r in rows]),4),'lossy_mem',sum(t is not None for t in t_lossy),
                                 'sec',round(time.monotonic()-start,1),flush=True)
            if step%5000==0:
                torch.save(dict(model=model.state_dict(),actor=actor.detach(),baseline=baseline,step=step,
                                receiver_optimizer=recopt.state_dict(),actor_optimizer=actopt.state_dict(),
                                rng_states=[r.bit_generator.state for r in rngs],histories=histories),target/f'checkpoint_{step}.pt')
                (target/'progress.json').write_text(json.dumps(dict(step=step,rows=rows),indent=2),encoding='utf-8')
            time.sleep(max(0.,.4-(time.monotonic()-block)));block=time.monotonic()
    results=[]
    for s in range(n):
        final=histories[s][-1];tl=t_lossy[s];tg=t_gen[s]
        candidate=family=='PRIVATE' and tl is not None and tg is not None and tg>=5*tl and tg-tl>=2000 and final['train']==1. and final['test']>=.95 and final['symbols']==31
        result=dict(seed=SEEDS[s],pair=s//2,support=support,family=family,final=final,history=histories[s],
                    t_mem=t_mem[s],t_gen=tg,t_mem_lossy=tl,capacity_expanding_delayed_candidate=bool(candidate))
        (target/f'metrics_s{SEEDS[s]}.json').write_text(json.dumps(result,indent=2),encoding='utf-8');results.append(result)
    del model,actor,recopt,actopt;torch.cuda.empty_cache()
    return results


def run():
    receipt=json.loads((BASE/'results/V190_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path,sha in receipt['source_sha256'].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==sha,path
    assert not json.loads((BASE/'results/V190_TECHNICAL_AUDIT.json').read_text(encoding='utf-8'))['failures']
    OUT.mkdir(exist_ok=False);torch.cuda.set_per_process_memory_fraction(.35)
    (OUT/'MANIFEST.json').write_text(json.dumps(dict(preregistration=receipt,context_pair_units=4,
        neural_histories_per_context_pair=2,torch=torch.__version__,device=torch.cuda.get_device_name()),indent=2),encoding='utf-8')
    results=[]
    for support in ['LOW','HIGH']:
        for family in ['FIXED_PROTOCOL','PRIVATE']:results.extend(train(support,family))
    positive={support:sum(r['final']['test']>=.95 for r in results if r['support']==support and r['family']=='FIXED_PROTOCOL')
              for support in ['LOW','HIGH']}
    candidates=[r for r in results if r['capacity_expanding_delayed_candidate']]
    gate=all(c>=6 for c in positive.values()) and len(candidates)>=4 and len({r['pair'] for r in candidates})>=2
    summary=dict(runs=[{k:v for k,v in r.items() if k!='history'} for r in results],positive_control_counts=positive,
                 candidate_count=len(candidates),candidate_context_pairs=sorted({r['pair'] for r in candidates}),
                 primary_gate_passed=bool(gate),new_learned_collective_mechanism_accredited=False,
                 mathematical_limits_designed_not_emergent=True,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V190_COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='runs'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['technical','run']);args=p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False
    {'technical':technical,'run':run}[args.command]()
