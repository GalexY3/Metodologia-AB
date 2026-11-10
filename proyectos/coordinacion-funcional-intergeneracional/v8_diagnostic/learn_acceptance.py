"""V8: neural acceptance as a falsifiable microtask.

Each of N agents owns independent logistic parameters. A provisional random
state change is visible to the actor via the SHARED public change in D. It
chooses to commit or revert. The only optimized reward is the common team's
actual progress; only the acting individual's score function gets updated.
The random proposal mechanism and serial activation schedule are scripted.
This is a learnability probe, NOT learned negotiation or full coordination.

Identical public reward for every agent, but only one agent acts per step.
No private/individual reward, shared parameters, global histogram features
or centralized critic.
"""
import argparse, json
from pathlib import Path
import numpy as np
from information_bottleneck import COLORS, distance

def sigmoid(x):
    x=np.clip(x,-20,20)
    return 1/(1+np.exp(-x))

def trial(n,k,batch,epochs,seed,weights,learn=False,lr=.03,mode="policy"):
    rng=np.random.default_rng(seed)
    colors=rng.integers(0,COLORS,(batch,n),dtype=np.int16)
    counts=np.stack([(colors==i).sum(axis=1) for i in range(COLORS)],axis=1)
    d=distance(counts,k)
    initial=d.copy()
    rows=np.arange(batch)
    for epoch in range(epochs):
        for actor in rng.permutation(n):
            old=colors[:,actor]
            proposed=rng.integers(0,COLORS,batch,dtype=np.int16)
            candidate_counts=counts.copy()
            np.add.at(candidate_counts,(rows,old),-1)
            np.add.at(candidate_counts,(rows,proposed),+1)
            trial_d=distance(candidate_counts,k)
            public_preliminary_gain=n*(d-trial_d)
            # Shared global provisional D delta available to all agents;
            # only actor i chooses and can be updated in this time slot.
            x=np.stack((public_preliminary_gain,np.ones(batch)),axis=-1)
            p=sigmoid(x@weights[actor])
            random_numbers=rng.random(batch)
            if mode=="scripted":
                accept=public_preliminary_gain>1e-10
            elif mode=="policy":
                accept=random_numbers<p
            elif mode=="greedy":
                accept=p>0.5
            else:raise ValueError(mode)
            reward=public_preliminary_gain*accept
            if learn:
                # REINFORCE with leave-one-world-out baseline, using COMMON
                # reward in each society. Independent theta_i, no weight sharing.
                baseline=(reward.sum()-reward)/max(1,batch-1)
                score=(accept.astype(float)-p)[:,None]*x
                grad=((reward-baseline)[:,None]*score).mean(0)
                weights[actor]+=lr*np.clip(grad,-2,2)
            counts[accept]=candidate_counts[accept]
            colors[accept,actor]=proposed[accept]
            d[accept]=trial_d[accept]
    top=np.sort(counts,axis=1)[:,-k:]/n
    leakage=1-top.sum(axis=1)
    overload=np.maximum(top-1/k,0).sum(axis=1)
    assert np.allclose(d,leakage+overload,atol=1e-10)
    return dict(initial_D=float(initial.mean()),final_D=float(d.mean()),
       leakage=float(leakage.mean()),overload=float(overload.mean()),
       exact=int(np.count_nonzero(d<1e-10)),worlds=batch,
       occupied=float(np.count_nonzero(counts,axis=1).mean()),
       final_distribution=np.histogram(np.count_nonzero(counts,axis=1),
                     bins=np.arange(0,COLORS+2))[0].tolist())

def train(n,k,batch,episodes,epochs,lr,seed):
    weights=np.zeros((n,2),dtype=float)
    history=[]
    for episode in range(episodes):
        result=trial(n,k,batch,epochs,seed+episode*9973,weights,True,lr)
        if episode==0 or (episode+1)%10==0 or episode==episodes-1:
            history.append(dict(episode=episode+1,mean_D=result["final_D"],
                                exact=result["exact"]))
    return weights,history

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--batch",type=int,default=64)
    p.add_argument("--episodes",type=int,default=30)
    p.add_argument("--train-epochs",type=int,default=3)
    p.add_argument("--eval-epochs",type=int,default=40)
    p.add_argument("--eval-worlds",type=int,default=80)
    p.add_argument("--lr",type=float,default=.03)
    p.add_argument("--seed",type=int,default=681104)
    args=p.parse_args()
    if args.batch<4 or args.episodes<1:raise ValueError("Increase batch/episodes")
    results=[]
    for n in (36,324):
        k=4
        for rep in range(3):
            seed=args.seed+100101*n+600000*rep
            theta,history=train(n,k,args.batch,args.episodes,
                           args.train_epochs,args.lr,seed)
            check=seed+9_000_000
            arms={}
            for name in ("untrained","trained","scripted"):
                w=np.zeros_like(theta) if name=="untrained" else theta.copy()
                arms[name]=trial(n,k,args.eval_worlds,args.eval_epochs,
                    check,w,mode="scripted" if name=="scripted" else "policy")
            probs=dict(positive=float(sigmoid(theta[:,0]+theta[:,1]).mean()),
                negative=float(sigmoid(-theta[:,0]+theta[:,1]).mean()),
                neutral=float(sigmoid(theta[:,1]).mean()),
                positive_gt_negative=float((theta[:,0]>0).mean()),
                std_weights=float(theta.std()))
            row=dict(n=n,k=k,repeat=rep,train_worlds=args.batch,
                  train_episodes=args.episodes,train_epochs=args.train_epochs,
                  evaluation_worlds=args.eval_worlds,eval_epochs=args.eval_epochs,
                  final_policies=probs,training_history=history,arms=arms)
            print("LEARNING",n,rep,"D",
              [(name,round(r["final_D"],4),r["exact"]) for name,r in arms.items()],
              "P+",round(probs["positive"],3),"P-",round(probs["negative"],3),
              flush=True)
            results.append(row)
    path=Path(__file__).resolve().parent/"RESULTS_V8_LEARNING_ACCEPTANCE.json"
    path.write_text(json.dumps(dict(kind="NEURAL_MICROTASK_NOT_FULL_COORDINATION",
        seed=args.seed,settings=vars(args),results=results),indent=2,
        ensure_ascii=False),encoding="utf-8")
    print("SAVED",path,flush=True)
if __name__=="__main__":main()
