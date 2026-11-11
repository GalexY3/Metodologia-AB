"""V17 regime inference: all features observed locally, reward contains a count side-channel.

A true occupation is only read for scoring, not for predictions. We compare
external-neighbor density with its hypergeometric correction and exact
integer-grid inversion of the INDIVIDUAL payoff. All ambiguity is explicit.
"""
from __future__ import annotations
import math,sys,json,os,itertools
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
import v12 as v12
torch.set_num_threads(3)
N=120
KS=(2,4,5,8,12,20,30,40,60)
MS=(12,24,40,80)
DS=(4,8,16)
TOPO=('ring','rewired')
INITS=('random','trap','cluster')
# Deterministic payoff-to-occupation inversion. Round float32 error conservatively.
def infer_reward(r,q,n=120,tol=2e-5):
    r=np.asarray(r,dtype=float)
    sub=q*r
    sup=q/np.maximum(r,1e-12)
    ok_sub=(sub>=1-1e-8)&(sub<q-1e-6)&(abs(sub-np.rint(sub))<tol)
    ok_sup=(sup>q+1e-6)&(sup<=n+1e-8)&(abs(sup-np.rint(sup))<tol)
    eq=(np.abs(r-1)<tol)
    unique_sub=ok_sub&(~ok_sup)
    unique_sup=ok_sup&(~ok_sub)
    certain=unique_sub|unique_sup|eq
    sign=np.where(unique_sub,-1,np.where(unique_sup,1,np.where(eq,0,2)))
    return sign,certain,ok_sub&ok_sup
def setup(c,seed,init):
    base=replace(c,init='trap' if init=='trap' else 'random')
    e=v12.World(base,seed)
    if init=='cluster':
        # Spatially segregated labels in the ring graph, 8 contiguous blocks;
        # no message / count information supplied to predictor.
        labels=torch.randperm(c.m,device=c.device)[:min(8,c.m)]
        jobs=labels[(torch.arange(c.n,device=c.device)*len(labels)//c.n)]
        e.jobs=jobs.unsqueeze(0).expand(c.batch,-1).clone()
        e.food,e.counts=v12.food(e.jobs,c.m,c.k)
        e.lastfood=e.food.clone()
    return e
def stats(e):
    c=e.c
    counts=e.counts.gather(1,e.jobs).detach().cpu().numpy()
    q=c.n/c.k
    truth=np.sign(counts-q).astype(int)
    local=e.local().gather(2,e.jobs[...,None]).squeeze(2).cpu().numpy()
    # NOTE: V12 local() ALREADY excludes self. No self-inclusion bias!
    naive=np.sign(c.k*local-1).astype(int)
    # Correct sampling expectation is (n_j - 1)/(N-1) on random mixing,
    # but spatial correlation violates that random-mixing assumption.
    corrected=np.sign(local-(q-1)/(c.n-1)).astype(int)
    reward=e.food.detach().cpu().numpy()
    exact,certain,ambiguous=infer_reward(reward,q,n=c.n)
    combined=np.where(certain,exact,corrected)
    return dict(
        exact_certain=float(certain.mean()),exact_ambiguous=float(ambiguous.mean()),
        exact_accuracy_when_certain=float(np.mean(exact[certain]==truth[certain])) if certain.any() else 0.,
        exact_plus_corrected=float(np.mean(combined==truth)),
        local_naive=float(np.mean(naive==truth)),
        local_hypergeom=float(np.mean(corrected==truth)),
        true_super=float(np.mean(truth==1)),true_sub=float(np.mean(truth==-1)),
        local_super_recall=float(np.mean(naive[truth==1]==1)) if (truth==1).any() else None,
        local_sub_recall=float(np.mean(naive[truth==-1]==-1)) if (truth==-1).any() else None,
        n_obs=truth.size
    )
def main():
    cases=[]
    for m,d,topology,init,k in itertools.product(MS,DS,TOPO,INITS,KS):
        if k>m:continue
        # Give simulations independent seeds per topology and category.
        c=v12.Config(n=N,m=m,k=k,degree=d,topology=topology,
                     batch=48,horizon=20,device='cpu')
        seed=11001+101*m+3*k+d+(2000 if topology=='rewired' else 0)+(10000 if init=='cluster' else 0)
        z=stats(setup(c,seed,init))
        cases.append(dict(m=m,k=k,degree=d,topology=topology,init=init,**z))
    out=HERE/'results'
    out.mkdir(parents=True,exist_ok=True)
    path=out/'regime_inference_v17.json'
    path.write_text(json.dumps(dict(n=N,n_cases=len(cases),cases=cases,
        interpretation='Reward inversion uses public N,k and individual food only; exact branch when integer candidate unique. Counts only evaluation labels. Neighbor observations exclude the focal node.'),indent=2),encoding='utf8')
    for init in INITS:
        zz=[r for r in cases if r['init']==init]
        for key in ('exact_certain','exact_accuracy_when_certain','exact_plus_corrected','local_naive','local_hypergeom'):
            vals=[v[key] for v in zz if v[key] is not None]
            print('SUMMARY',init,key,round(float(np.mean(vals)),4),'Ncases',len(vals),flush=True)
    for k in (4,12,30,60):
        for init in INITS:
            zz=[r for r in cases if r['k']==k and r['init']==init and r['m']==80 and r['degree']==8 and r['topology']=='ring']
            if zz:
                x=zz[0]
                print('DETAIL','k',k,'init',init,'reward_certain',round(x['exact_certain'],4),
                 'local',round(x['local_naive'],4),'corrected',round(x['local_hypergeom'],4),
                 'hybrid',round(x['exact_plus_corrected'],4),flush=True)
    print('REGIME_COMPLETE',len(cases),'cases',sum(x['n_obs'] for x in cases),'agent-observations',flush=True)
if __name__=='__main__':main()
