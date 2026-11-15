"""Independent histories batched on GPU; classical sender urns, neural receivers.

No cross-agent gradients. Known signaling mechanisms adapted to the existing
modular task. Batching is an arithmetic optimization, not parameter sharing.
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
from v185_collective_grokking import Receiver,split,P,H
from v187_classical_signaling import choose,add_token

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V188_PRIVATE_CONVENTIONS'
SEEDS=list(range(188115,188123))
CAP=int(1.4*P*P)
STEPS=30000


class BatchedReceiver(nn.Module):
    def __init__(self,seeds,dtype=torch.float32,device='cpu'):
        super().__init__()
        models=[]
        for seed in seeds:
            torch.manual_seed(seed)
            models.append(Receiver().to(dtype=dtype))
        self.message=nn.Parameter(torch.stack([r.message.weight.detach() for r in models]).to(device))
        self.context=nn.Parameter(torch.stack([r.context.weight.detach() for r in models]).to(device))
        self.output=nn.Parameter(torch.stack([r.output.weight.detach().T for r in models]).contiguous().to(device))

    def forward(self,messages,b):
        index=torch.arange(len(self.message),device=self.message.device)[:,None]
        hidden=self.message[index,messages]+self.context[index,b]
        return torch.bmm(hidden.square(),self.output)


@njit(cache=True)
def sample_messages(policies,a,coins):
    messages=np.zeros((len(policies),len(a)),dtype=np.int64)
    for s in range(len(policies)):
        for i in range(len(a)):messages[s,i]=choose(policies[s,a[i]],coins[s,i])
    return messages


@njit(cache=True)
def normalized_counts(counts):
    policies=np.zeros(counts.shape,dtype=np.float64)
    for s in range(len(counts)):
        for a in range(counts.shape[1]):
            total=counts[s,a].sum()
            for m in range(counts.shape[2]):policies[s,a,m]=counts[s,a,m]/total if total else 1./counts.shape[2]
    return policies


@njit(cache=True)
def update_urns(counts,bags,sizes,a,messages,rewards,coins,limited):
    for s in range(len(counts)):
        order=np.argsort(coins[s,:,2])
        for i in order:
            if rewards[s,i]>0:
                add_token(counts,bags,sizes,s,a[i],messages[s,i],coins[s,i,1],limited)


def new_urns(n):
    counts=np.ones((n,P,P),dtype=np.int64)
    bags=np.full((n,CAP,2),-1,dtype=np.int64)
    pairs=np.array([(a,m) for a in range(P) for m in range(P)],dtype=np.int64)
    bags[:,:P*P]=pairs
    return counts,bags,np.full(n,P*P,dtype=np.int64)


def technical():
    seeds=[188901,188902]
    batch=BatchedReceiver(seeds,dtype=torch.float64)
    individuals=[]
    for seed in seeds:
        torch.manual_seed(seed);individuals.append(Receiver().double())
    rng=np.random.default_rng(188900)
    m=torch.tensor(rng.integers(P,size=(2,47)))
    b=torch.tensor(rng.integers(P,size=(2,47)))
    y=torch.tensor(rng.integers(P,size=(2,47)))
    logits=batch(m,b)
    separate=torch.stack([r(m[s],b[s]) for s,r in enumerate(individuals)])
    checks=[dict(field='forward',error=float((logits-separate).abs().max().detach()),tolerance=1e-10)]
    loss=nn.functional.cross_entropy(logits.reshape(-1,P),y.reshape(-1),reduction='none').reshape(2,-1).mean(1).sum()
    loss.backward()
    for s,r in enumerate(individuals):nn.functional.cross_entropy(separate[s],y[s]).backward(retain_graph=s==0)
    for key,attribute in [('message','message'),('context','context'),('output','output')]:
        expected=torch.stack([getattr(r,attribute).weight.grad if key!='output' else r.output.weight.grad.T for r in individuals])
        checks.append(dict(field='gradient_'+key,error=float((getattr(batch,key).grad-expected).abs().max()),tolerance=1e-10))
    opt=torch.optim.AdamW(batch.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98))
    opt.step()
    for r in individuals:torch.optim.AdamW(r.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98)).step()
    for key,attribute in [('message','message'),('context','context'),('output','output')]:
        expected=torch.stack([getattr(r,attribute).weight.detach() if key!='output' else r.output.weight.detach().T for r in individuals])
        checks.append(dict(field='AdamW_'+key,error=float((getattr(batch,key)-expected).abs().max().detach()),tolerance=1e-10))
    batch.zero_grad(set_to_none=True)
    nn.functional.cross_entropy(batch(m,b)[0],y[0]).backward()
    checks.append(dict(field='other_history_gradient',error=max(float(p.grad[1].abs().max()) for p in batch.parameters()),tolerance=0))
    # Sender objective uses only detached scalar feedback, not the receiver graph.
    batch.zero_grad(set_to_none=True)
    actor=nn.Parameter(torch.zeros((2,P,P),dtype=torch.float64))
    aa=torch.tensor(rng.integers(P,size=47))
    logp=actor[:,aa].log_softmax(2)
    reward=torch.tensor((np.arange(47)%3==0).astype(float))[None].repeat(2,1)
    sender_loss=-(reward*logp.gather(2,m[:,:,None]).squeeze(2)).mean(1).sum()
    sender_loss.backward()
    assert all(p.grad is None for p in batch.parameters()) and actor.grad.abs().sum()>0
    # Batch urn update versus a direct list-of-tokens interpreter.
    counts,bags,sizes=new_urns(2)
    memories=[[tuple(x) for x in bags[s,:P*P]] for s in range(2)]
    expected=counts.copy()
    for step in range(40):
        a=rng.integers(P,size=73);policies=normalized_counts(counts);coins=rng.random((2,len(a),3))
        got=sample_messages(policies,a,coins[:,:,0])
        reference=np.array([[np.searchsorted(np.cumsum(policies[s,a[i]]),coins[s,i,0],side='right') for i in range(len(a))] for s in range(2)])
        assert np.array_equal(got,reference)
        rewards=(rng.random((2,len(a)))<.7).astype(float)
        update_urns(counts,bags,sizes,a,got,rewards,coins,True)
        for s in range(2):
            for i in np.argsort(coins[s,:,2]):
                if not rewards[s,i]:continue
                pair=(int(a[i]),int(got[s,i]))
                if len(memories[s])==CAP:
                    ix=int(coins[s,i,1]*CAP);old=memories[s][ix]
                    expected[s,old[0],old[1]]-=1;memories[s][ix]=pair
                else:memories[s].append(pair)
                expected[s,pair[0],pair[1]]+=1
        assert np.array_equal(counts,expected)
        assert np.all(counts.sum(axis=(1,2))==sizes) and np.max(sizes)<=CAP
    for c in checks:c['passed']=c['error']<=c['tolerance']
    result=dict(checks=checks,failures=[c for c in checks if not c['passed']],urn_list_reference_batches=40,
                actor_gradient_isolation=True,no_parameters_shared_between_histories=True,
                scientific_training_executed=False)
    (BASE/'results/V188_TECHNICAL_AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)
    assert not result['failures']


@torch.no_grad()
def evaluate(model,policies,dictionaries,full,mask):
    a,b,y=full;n=len(policies);device=policies.device
    protocol=policies.argmax(2) if dictionaries is None else dictionaries
    messages=protocol[:,a]
    logits=model(messages,b[None].expand(n,-1))
    correct=logits.argmax(2)==y[None]
    train=torch.tensor(mask.ravel(),device=device)
    all_m,all_b=np.indices((P,P))
    mm=torch.tensor(all_m.ravel(),device=device)[None].expand(n,-1)
    bb=torch.tensor(all_b.ravel(),device=device)[None].expand(n,-1)
    predictions=model(mm,bb).argmax(2).reshape(n,P,P)
    targets=(torch.arange(P,device=device)[:,None]+torch.arange(P,device=device)[None,:])%P
    event=(predictions[:,None,:,:]==targets[None,:,None,:]).float()
    expected=(policies[:,:,:,None]*event).sum(2).reshape(n,-1)
    onehot=nn.functional.one_hot(protocol,P).float().transpose(1,2)
    test_counts=onehot@torch.tensor((~mask).astype(float),device=device,dtype=torch.float32)
    rows=[]
    for s in range(n):
        rows.append(dict(train=float(correct[s,train].float().mean()),test=float(correct[s,~train].float().mean()),
                         train_expected=float(expected[s,train].mean()),test_expected=float(expected[s,~train].mean()),
                         train_nll=float(nn.functional.cross_entropy(logits[s,train],y[train])),
                         test_nll=float(nn.functional.cross_entropy(logits[s,~train],y[~train])),
                         protocol_symbols=int(protocol[s].unique().numel()),
                         entropy=float(-(policies[s]*policies[s].clamp_min(1e-12).log()).sum(1).mean()),
                         bayes_bound_full_stochastic=float(policies[s].max(0).values.sum()/P),
                         bayes_bound_test_greedy=float((test_counts[s]>0).float().sum()/(~mask).sum())))
    return rows


def extract_optimizer(optimizer,seed_index):
    state=copy.deepcopy(optimizer.state_dict())
    for values in state['state'].values():
        for key,value in list(values.items()):
            if isinstance(value,torch.Tensor) and value.ndim>0:values[key]=value[seed_index:seed_index+1].clone()
    return state


def train_family(family):
    directory=OUT/family;directory.mkdir(exist_ok=False)
    n=len(SEEDS);device='cuda'
    model=BatchedReceiver(SEEDS,device=device)
    receiver_optim=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98))
    actor=nn.Parameter(torch.zeros((n,P,P),device=device))
    actor_optim=torch.optim.Adam([actor],lr=.03)
    counts,bags,sizes=new_urns(n)
    rngs=[np.random.default_rng(seed+10000) for seed in SEEDS]
    mask,aa,bb,yy=split()
    full=tuple(torch.tensor(v,dtype=torch.long,device=device) for v in (aa,bb,yy))
    trainmask=mask.ravel();a_np=aa[trainmask]
    a,b,y=(v[torch.tensor(trainmask,device=device)] for v in full)
    obs_counts=torch.bincount(a,minlength=P).float()
    group_matrix=nn.functional.one_hot(a,P).float().T/obs_counts[:,None]
    baseline=torch.zeros((n,P),device=device)
    dictionaries=None
    if family=='FIXED_PROTOCOL':
        dictionaries=torch.tensor(np.stack([np.random.default_rng(s+20000).permutation(P) for s in SEEDS]),device=device)
    histories=[[] for _ in SEEDS];t_mem=[None]*n;t_gen=[None]*n;sm=[0]*n;sg=[0]*n;sc=[0]*n;causal_saved=[False]*n
    started=time.monotonic();block_started=started
    for step in range(1,STEPS+1):
        # Fixed draw budget for each history and each method, including unused coins.
        coins=np.stack([rng.random((len(a_np),3)) for rng in rngs])
        actor_log_probs=actor[:,a].log_softmax(2)
        if family=='REINFORCE':policies=actor.softmax(2);prob_np=policies.detach().cpu().double().numpy()
        elif family=='FIXED_PROTOCOL':policies=nn.functional.one_hot(dictionaries,P).float();prob_np=policies.cpu().double().numpy()
        else:
            prob_np=normalized_counts(counts)
            policies=torch.tensor(prob_np,device=device,dtype=torch.float32)
        messages_np=sample_messages(prob_np,a_np,coins[:,:,0])
        messages=torch.tensor(messages_np,device=device)
        logits=model(messages,b[None].expand(n,-1))
        reward=(logits.detach().argmax(2)==y[None]).float()
        receiver_optim.zero_grad(set_to_none=True)
        loss=nn.functional.cross_entropy(logits.reshape(-1,P),y[None].expand(n,-1).reshape(-1),reduction='none').reshape(n,-1).mean(1).sum()
        loss.backward();receiver_optim.step()
        if family=='REINFORCE':
            advantage=(reward-baseline[:,a]).detach()
            entropy=-(actor_log_probs.exp()*actor_log_probs).sum(2).mean(1).sum()
            actor_loss=-(advantage*actor_log_probs.gather(2,messages[:,:,None]).squeeze(2)).mean(1).sum()-.01*entropy
            actor_optim.zero_grad(set_to_none=True);actor_loss.backward();actor_optim.step()
        elif family.startswith('URN_'):
            update_urns(counts,bags,sizes,a_np,messages_np,reward.cpu().numpy(),coins,family=='URN_LIMITED')
        baseline=.95*baseline+.05*(reward@group_matrix.T).detach()
        if step%100==0:
            if family=='REINFORCE':policies=actor.softmax(2)
            elif family.startswith('URN_'):policies=torch.tensor(normalized_counts(counts),device=device,dtype=torch.float32)
            rows=evaluate(model,policies,dictionaries,full,mask)
            for s,row in enumerate(rows):
                row['step']=step;histories[s].append(row)
                sm[s]=sm[s]+1 if row['train']>=.99 else 0
                sg[s]=sg[s]+1 if row['test']>=.95 else 0
                sc[s]=sc[s]+1 if row['train']>=.99 and row['protocol_symbols']==P else 0
                if t_mem[s] is None and sm[s]>=5:t_mem[s]=step
                if t_gen[s] is None and sg[s]>=5:t_gen[s]=step
                if family.startswith('URN_') and not causal_saved[s] and sc[s]>=5:
                    snapshot=dict(seed=SEEDS[s],family=family,step=step,
                                  model={k:v[s:s+1].detach().clone() for k,v in model.state_dict().items()},
                                  receiver_optimizer=extract_optimizer(receiver_optim,s),
                                  counts=counts[s:s+1].copy(),bags=bags[s:s+1].copy(),sizes=sizes[s:s+1].copy(),
                                  policies=policies[s:s+1].detach().clone(),rng_state=copy.deepcopy(rngs[s].bit_generator.state),
                                  baseline=baseline[s:s+1].detach().clone(),history=copy.deepcopy(histories[s]),
                                  selection_uses_test=False)
                    torch.save(snapshot,directory/f'causal_checkpoint_s{SEEDS[s]}.pt');causal_saved[s]=True
            if step%1000==0:
                print('V188',family,step,'train',round(np.mean([r['train'] for r in rows]),4),
                      'test',round(np.mean([r['test'] for r in rows]),4),
                      'expected_test',round(np.mean([r['test_expected'] for r in rows]),4),
                      'sec',round(time.monotonic()-started,1),flush=True)
            if step%5000==0:
                torch.save(dict(model=model.state_dict(),receiver_optimizer=receiver_optim.state_dict(),actor=actor.detach(),
                                actor_optimizer=actor_optim.state_dict(),counts=counts,bags=bags,sizes=sizes,
                                rng_states=[r.bit_generator.state for r in rngs],baseline=baseline,step=step,histories=histories),
                           directory/f'checkpoint_{step}.pt')
                (directory/'progress.json').write_text(json.dumps(dict(step=step,rows=rows),indent=2),encoding='utf-8')
            # Give the desktop regular idle windows. This changes wall time only.
            time.sleep(max(0.,.4-(time.monotonic()-block_started)))
            block_started=time.monotonic()
    results=[]
    for s,seed in enumerate(SEEDS):
        final=histories[s][-1]
        delayed=t_mem[s] is not None and t_gen[s] is not None and final['test']>=.95 and t_gen[s]>=5*t_mem[s] and t_gen[s]-t_mem[s]>=2000
        result=dict(seed=seed,family=family,final=final,history=histories[s],t_mem=t_mem[s],t_gen=t_gen[s],
                    delayed_generalization=bool(delayed),causal_checkpoint_saved=causal_saved[s])
        (directory/f'metrics_s{seed}.json').write_text(json.dumps(result,indent=2),encoding='utf-8');results.append(result)
    del model,receiver_optim,actor,actor_optim
    torch.cuda.empty_cache()
    return results


def run():
    receipt=json.loads((BASE/'results/V188_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path,expected in receipt['source_sha256'].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==expected,path
    assert json.loads((BASE/'results/V187_CLASSICAL_SIGNALING/SUMMARY.json').read_text(encoding='utf-8'))['competence_gate_passed']
    technical_report=json.loads((BASE/'results/V188_TECHNICAL_AUDIT.json').read_text(encoding='utf-8'))
    assert not technical_report['failures'] and technical_report['actor_gradient_isolation']
    torch.cuda.set_per_process_memory_fraction(.35)
    OUT.mkdir(exist_ok=False)
    manifest=dict(preregistration=receipt,torch=torch.__version__,numpy=np.__version__,device=torch.cuda.get_device_name(),
                  CPU_threads=2,independent_parameter_slices=8,sender_memory_cap=CAP,known_test_from_V185=True)
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    results=[]
    for family in ['FIXED_PROTOCOL','REINFORCE','URN_PURE','URN_LIMITED']:results.extend(train_family(family))
    limited=[r for r in results if r['family']=='URN_LIMITED'];pg=[r for r in results if r['family']=='REINFORCE']
    differences=[a['final']['test']-b['final']['test'] for a,b in zip(limited,pg)]
    count=sum(r['final']['test']>=.95 and r['final']['test_expected']>=.9 for r in limited)
    summary=dict(runs=[{k:v for k,v in r.items() if k!='history'} for r in results],limited_qualified=count,
                 limited_minus_REINFORCE_test=differences,median_advantage=float(np.median(differences)),
                 primary_gate_passed=bool(count>=6 and np.median(differences)>=.2),
                 independent_seed_blocks=8,training_runs=32,collective_grokking_established=False,
                 known_mechanism_not_new_institution=True,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V188_COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='runs'}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['technical','run'])
    args=parser.parse_args();print('LIMITS',apply_limits(2),flush=True)
    torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False
    {'technical':technical,'run':run}[args.command]()
