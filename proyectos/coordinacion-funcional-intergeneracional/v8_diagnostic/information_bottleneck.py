"""V8 diagnostic: global feedback identifiability and simultaneous-action noise.

This is not policy training. The focal action is selected by an oracle using
the global histogram only for OFFLINE diagnostic counterfactuals; no agent
ever receives this information as a training input. All other actors choose
new states uniformly, independently, if scheduled to act.

Outputs report the signal-to-noise of public global progress when the number
of simultaneous mutations varies. The inferred oracle advantage is not an
individual reward used for training.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np

COLORS=10

def distance(counts,k):
    """TV distance to nearest equal k-supported distribution, M=10."""
    x=np.asarray(counts)
    n=x.sum(axis=-1)
    top=np.sort(x,axis=-1)[...,-k:]
    return 1-np.minimum(top,n[...,None]/k).sum(-1)/n

def ambiguous_example():
    """Same local view and public D; focal action requires opposite choices."""
    a=np.array([17,19]+[0]*8)
    b=np.array([19,17]+[0]*8)
    aa=a.copy(); bb=b.copy()
    aa[0]-=1;aa[1]+=1
    bb[0]-=1;bb[1]+=1
    assert distance(a,2)==distance(b,2)
    assert distance(aa,2)>distance(a,2)
    assert distance(bb,2)<distance(b,2)
    return dict(n=36,k=2,focal_color=0,neighbors=[0]*5,
      global_D=float(distance(a,2)),society_A=dict(counts=a.tolist(),
      after=aa.tolist(),error_after=float(distance(aa,2))),
      society_B=dict(counts=b.tolist(),after=bb.tolist(),
      error_after=float(distance(bb,2))))

def sample_oracle_move(colors,counts,k,rng):
    """Choose from outside current top k to an under-quota top color."""
    batch,n=colors.shape
    ordered=np.argsort(-counts,axis=1,kind="stable")
    top=ordered[:,:k]
    focal=np.zeros(batch,dtype=np.int64)
    destination=np.zeros(batch,dtype=np.int64)
    valid=np.ones(batch,dtype=bool)
    for i in range(batch):
        eligible=top[i][counts[i,top[i]]<n/k]
        outsiders=np.flatnonzero(~np.isin(colors[i],top[i]))
        if len(eligible)==0 or len(outsiders)==0:
            valid[i]=False
            continue
        focal[i]=rng.choice(outsiders)
        destination[i]=eligible[np.argmax(counts[i,eligible])]
    return focal,destination,valid

def diagnostic(n,k,samples,seed):
    rng=np.random.default_rng(seed)
    colors=rng.integers(0,COLORS,(samples,n),dtype=np.int16)
    counts=np.stack([(colors==color).sum(-1) for color in range(COLORS)],axis=-1)
    focal,target,valid=sample_oracle_move(colors,counts,k,rng)
    colors,counts,focal,target=colors[valid],counts[valid],focal[valid],target[valid]
    b=colors.shape[0]
    if b==0:raise RuntimeError("No valid diagnostic worlds")
    arange=np.arange(b)
    source=colors[arange,focal]
    initial_D=distance(counts,k)
    levels=sorted(set([1,2,4,8,16,32,64,128,n]))
    levels=[x for x in levels if x<=n]
    data=[]
    for m in levels:
        modified=counts.copy()
        if m>1:
            # Sample distinct agents other than focal, independently by world.
            keys=rng.random((b,n),dtype=np.float32)
            keys[arange,focal]=2.0
            selected=np.argpartition(keys,m-2,axis=1)[:,:m-1]
            old=colors[arange[:,None],selected]
            new=rng.integers(0,COLORS,(b,m-1),dtype=np.int16)
            rr=np.broadcast_to(arange[:,None],old.shape)
            np.add.at(modified,(rr.ravel(),old.ravel()),-1)
            np.add.at(modified,(rr.ravel(),new.ravel()),+1)
        d_random=distance(modified,k)
        treatment=modified.copy()
        np.add.at(treatment,(arange,source),-1)
        np.add.at(treatment,(arange,target),+1)
        d_after=distance(treatment,k)
        noise=n*(initial_D-d_random)
        contribution=n*(d_random-d_after)
        observed=n*(initial_D-d_after)
        noise_sd=float(noise.std(ddof=1)) if b>1 else 0
        snr=float(contribution.mean()/noise_sd) if noise_sd>1e-8 else None
        data.append(dict(concurrent_actors=m,worlds=b,
            mean_single_agent_causal_effect=float(contribution.mean()),
            public_reward_noise_sd=noise_sd,
            public_progress_snr=snr,
            probability_observed_global_improvement=float((observed>1e-6).mean()),
            probability_observed_global_deterioration=float((observed<-1e-6).mean()),
            probability_observed_global_no_change=float((abs(observed)<=1e-6).mean()),
            mean_global_progress=float(observed.mean())))
    return dict(n=n,k=k,samples=b,initial_D=float(initial_D.mean()),levels=data)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--samples",type=int,default=2000)
    p.add_argument("--seed",type=int,default=62511)
    p.add_argument("--output",default="RESULTS_V8_SIGNAL.json")
    args=p.parse_args()
    if args.samples<10:raise ValueError("Need >=10 samples")
    rows=[]
    for n in (36,144,324):
        for k in (2,3,4):
            r=diagnostic(n,k,args.samples,args.seed+n*1009+k*307)
            rows.append(r)
            preview=[(e["concurrent_actors"],round(e["public_progress_snr"],3) if e["public_progress_snr"] is not None else "undefined")
                      for e in r["levels"]]
            print("DIAGNOSTIC",n,k,"N",r["samples"],"SNR",preview,flush=True)
    out=dict(kind="offline_diagnostic_not_training",initial_public_example=ambiguous_example(),
             seed=args.seed,requested_samples=args.samples,
             experiment="Random simultaneous other-agent actions; oracle-selected single mutation; observational public Delta D.",
             rows=rows)
    path=Path(__file__).resolve().parent/args.output
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print("SAVED",path)
if __name__=="__main__":main()
