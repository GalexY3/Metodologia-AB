"""V8 SCRIPTED upper-bound control, not an RL model and not learned cooperation.

A public signal announces change of global D after an attempted action.
For m=1, a single scheduled agent chooses an arbitrary new state, accepts
only when public D improves, otherwise reverts. The agent needs only its
own color, proposed color, and public progress. No one sees the census.

For m>1, m actors propose simultaneously and ALL follow the same publicly
announced accept/revert rule. This is a scripted convention, not emergence.
All conditions receive the same number of attempted individual changes.
"""
from __future__ import annotations
import json, argparse
from pathlib import Path
import numpy as np
from information_bottleneck import distance, COLORS

def run_one(n,k,m,worlds,epochs,seed):
    rng=np.random.default_rng(seed)
    colors=rng.integers(0,COLORS,(worlds,n),dtype=np.int16)
    counts=np.stack([(colors==i).sum(1) for i in range(COLORS)],axis=1)
    D=distance(counts,k)
    initial=float(D.mean())
    b=np.arange(worlds)
    attempts=accepted_rounds=0
    curve=[dict(epoch=0,mean_D=initial,exact=int(np.count_nonzero(D<1e-9)),
                occupied=float(np.count_nonzero(counts,axis=1).mean()))]
    for epoch in range(1,epochs+1):
        indices=rng.permutation(n)
        for off in range(0,n,m):
            idx=indices[off:off+m]
            group=idx.size
            old=colors[:,idx]
            candidate=rng.integers(0,COLORS,(worlds,group),dtype=np.int16)
            modified=counts.copy()
            rr=np.broadcast_to(b[:,None],old.shape)
            np.add.at(modified,(rr.ravel(),old.ravel()),-1)
            np.add.at(modified,(rr.ravel(),candidate.ravel()),+1)
            next_D=distance(modified,k)
            accept=next_D<D-1e-10
            counts[accept]=modified[accept]
            D[accept]=next_D[accept]
            # Assign only the selected actor positions in accepting societies.
            if accept.any():
                rows=np.flatnonzero(accept)
                colors[rows[:,None],idx[None,:]]=candidate[rows]
            attempts+=worlds*group
            accepted_rounds+=int(accept.sum())
        curve.append(dict(epoch=epoch,mean_D=float(D.mean()),
          exact=int(np.count_nonzero(D<1e-9)),
          occupied=float(np.count_nonzero(counts,axis=1).mean())))
    return dict(n=n,k=k,concurrent=m,worlds=worlds,epochs=epochs,
      proposals=attempts,initial_D=initial,final_D=float(D.mean()),
      exact=int(np.count_nonzero(D<1e-9)),fraction_exact=float((D<1e-9).mean()),
      occupied=float(np.count_nonzero(counts,axis=1).mean()),
      successful_collective_rounds=accepted_rounds,
      trajectory=curve)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--worlds",type=int,default=40)
    p.add_argument("--epochs",type=int,default=25)
    p.add_argument("--seed",type=int,default=40557)
    args=p.parse_args()
    out=[]
    for n in (36,144,324):
        for k in (2,3,4):
            for m in (1,4,n):
                r=run_one(n,k,m,args.worlds,args.epochs,
                          args.seed+3001*n+41*k)
                out.append(r)
                print("CONTROLLER",n,k,"m",m,"D",round(r["initial_D"],4),
                  "=>",round(r["final_D"],4),"EXACT",r["exact"],"/",args.worlds,
                  "OCC",round(r["occupied"],3),flush=True)
    path=Path(__file__).resolve().parent/"RESULTS_V8_CONTROLLER.json"
    path.write_text(json.dumps(dict(kind="SCRIPTED_CONTROL_NOT_NEURAL",
      explanation="Sequential/simultaneous random proposals and public accept-if-D-improves; no trained agents.",
      seed=args.seed,worlds=args.worlds,epochs=args.epochs,rows=out),
      indent=2),encoding="utf-8")
    print("SAVED",path)
if __name__=="__main__":main()
