"""Paper-based reimplementation of a known signaling/limited-memory effect.

Original linked code is unavailable (404). Uniform sampling for an empty row
or column is an explicit operational completion, not an audited source detail.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
from numba import njit
from research_resource_limits import apply_limits

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V187_CLASSICAL_SIGNALING'


@njit(cache=True)
def choose(weights,u):
    total=weights.sum()
    if total==0:return min(len(weights)-1,int(u*len(weights)))
    target=u*total
    cumulative=0
    for i in range(len(weights)):
        cumulative+=weights[i]
        if target<cumulative:return i
    return len(weights)-1


@njit(cache=True)
def add_token(counts,bags,sizes,agent,meaning,symbol,u,limited):
    if limited:
        cap=bags.shape[1]
        if sizes[agent]<cap:
            location=sizes[agent]
            sizes[agent]+=1
        else:
            location=min(cap-1,int(u*cap))
            old_m,old_s=bags[agent,location]
            counts[agent,old_m,old_s]-=1
        bags[agent,location,0]=meaning
        bags[agent,location,1]=symbol
    counts[agent,meaning,symbol]+=1


@njit(cache=True)
def accuracy(counts):
    agents,p,_=counts.shape
    production=np.zeros_like(counts,dtype=np.float64)
    reception=np.zeros_like(counts,dtype=np.float64)
    for agent in range(agents):
        for m in range(p):
            total=counts[agent,m,:].sum()
            for s in range(p):production[agent,m,s]=counts[agent,m,s]/total if total else 1./p
        for s in range(p):
            total=counts[agent,:,s].sum()
            for m in range(p):reception[agent,m,s]=counts[agent,m,s]/total if total else 1./p
    result=0.
    for a in range(agents):
        for b in range(agents):
            if a==b:continue
            for m in range(p):
                for s in range(p):result+=production[a,m,s]*reception[b,m,s]
    return result/(agents*(agents-1)*p)


@njit(cache=True)
def simulate(tape,limited):
    agents,p,cap=10,5,35
    counts=np.ones((agents,p,p),dtype=np.int64)
    bags=np.full((agents,cap,2),-1,dtype=np.int64)
    sizes=np.full(agents,p*p,dtype=np.int64)
    for a in range(agents):
        index=0
        for m in range(p):
            for s in range(p):
                bags[a,index,0]=m;bags[a,index,1]=s;index+=1
    success=np.zeros(len(tape),dtype=np.bool_)
    checkpoints=np.full(4,np.nan)
    for t in range(len(tape)):
        u=tape[t]
        speaker=min(agents-1,int(u[0]*agents))
        hearer=min(agents-2,int(u[1]*(agents-1)))
        if hearer>=speaker:hearer+=1
        meaning=min(p-1,int(u[2]*p))
        signal=choose(counts[speaker,meaning,:],u[3])
        guess=choose(counts[hearer,:,signal],u[4])
        correct=meaning==guess
        success[t]=correct
        if correct:
            add_token(counts,bags,sizes,speaker,meaning,signal,u[5],limited)
            add_token(counts,bags,sizes,hearer,meaning,signal,u[6],limited)
        for j,checkpoint in enumerate((100,1000,5000,20000)):
            if t+1==checkpoint:checkpoints[j]=accuracy(counts)
    return counts,bags,sizes,success,checkpoints


def reference(tape,limited):
    counts=np.ones((10,5,5),dtype=np.int64)
    memories=[[(m,s) for m in range(5) for s in range(5)] for _ in range(10)]
    successes=[]
    for u in tape:
        speaker=int(u[0]*10);hearer=int(u[1]*9)
        if hearer>=speaker:hearer+=1
        meaning=int(u[2]*5)
        weights=counts[speaker,meaning,:]
        signal=int(np.searchsorted(np.cumsum(weights),u[3]*weights.sum(),side='right')) if weights.sum() else int(u[3]*5)
        weights=counts[hearer,:,signal]
        guess=int(np.searchsorted(np.cumsum(weights),u[4]*weights.sum(),side='right')) if weights.sum() else int(u[4]*5)
        correct=meaning==guess;successes.append(correct)
        if correct:
            for agent,coin in [(speaker,u[5]),(hearer,u[6])]:
                if limited:
                    if len(memories[agent])==35:
                        index=int(coin*35)
                        m,s=memories[agent][index];counts[agent,m,s]-=1
                        memories[agent][index]=(meaning,signal)
                    else:memories[agent].append((meaning,signal))
                counts[agent,meaning,signal]+=1
    bags=np.full((10,35,2),-1,dtype=np.int64)
    for a,memory in enumerate(memories):bags[a,:len(memory)]=memory
    return counts,bags,np.array([len(m) for m in memories]),np.array(successes)


def technical():
    checks=[]
    for seed in [187901,187902,187903]:
        tape=np.random.default_rng(seed).random((1024,7))
        for limited in [False,True]:
            for length in [1,16,64,256,1024]:
                got=simulate(tape[:length],limited)
                expected=reference(tape[:length],limited)
                for field in range(4):
                    same=np.array_equal(got[field],expected[field])
                    checks.append(dict(seed=seed,limited=limited,steps=length,field=field,passed=bool(same)))
                if limited:
                    assert np.all(got[0].sum(axis=(1,2))==got[2]) and np.max(got[2])<=35
    for coin in [0.,.01,.5,.999999]:
        assert choose(np.zeros(5,dtype=np.int64),coin)==int(coin*5)
    result=dict(checks=checks,failures=[r for r in checks if not r['passed']],
                independent_Python_NumPy_reference=True,original_author_code_executed=False,
                no_new_scientific_campaign_run=True)
    (BASE/'results/V187_TECHNICAL_AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('TECHNICAL',len(checks),'checks',len(result['failures']),'failures',flush=True)
    assert not result['failures']


def run():
    receipt=json.loads((BASE/'results/V187_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_campaign'] and receipt['remote_commit']
    for path,expected in receipt['source_sha256'].items():
        assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==expected,path
    assert not json.loads((BASE/'results/V187_TECHNICAL_AUDIT.json').read_text(encoding='utf-8'))['failures']
    OUT.mkdir(exist_ok=False)
    (OUT/'SOURCE_MANIFEST.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    rows=[];started=time.monotonic()
    for seed in range(187001,187101):
        tape=np.random.default_rng(seed).random((20000,7))
        for name,limited in [('PURE',False),('LIMITED35',True)]:
            counts,bags,sizes,success,trajectory=simulate(tape,limited)
            value=float(accuracy(counts))
            np.savez_compressed(OUT/f'{name}_s{seed}.npz',counts=counts,bags=bags,sizes=sizes,success=success,
                                checkpoints=trajectory,tape_seed=seed)
            rows.append(dict(seed=seed,condition=name,accuracy=value,checkpoints=trajectory.tolist(),
                             exact_normalization=True,optimal99=bool(value>=.99)))
        if seed%10==0:print('CALIBRATION',seed-187000,'/100','sec',round(time.monotonic()-started,1),flush=True)
    pure=[r for r in rows if r['condition']=='PURE'];limited=[r for r in rows if r['condition']=='LIMITED35']
    difference=float(np.mean([r['accuracy'] for r in limited])-np.mean([r['accuracy'] for r in pure]))
    n=sum(r['optimal99'] for r in limited)
    summary=dict(rows=rows,limited99_count=n,pure99_count=sum(r['optimal99'] for r in pure),
                 mean_limited=float(np.mean([r['accuracy'] for r in limited])),
                 mean_pure=float(np.mean([r['accuracy'] for r in pure])),mean_difference=difference,
                 competence_gate_passed=bool(n>=80 and difference>=.05),original_code_available=False,
                 independent_paper_based_reimplementation=True,originality_claimed=False,
                 CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('CALIBRATION_COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='rows'}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['technical','run'])
    args=parser.parse_args();print('LIMITS',apply_limits(2),flush=True)
    {'technical':technical,'run':run}[args.command]()
