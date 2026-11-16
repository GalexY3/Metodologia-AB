"""Private acquisition of voluntary relational payments; fixed roles and capital.

No enforcement, fine, prescribed donor, utility sharing or policy sharing.
Geometric relationship termination (p=.05) implements beta=.95 WITHOUT a
second discount in updates. Policies persist across fresh relationships.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from numba import njit

B=Path(__file__).resolve().parent
STOCK=.8903152454708944
F=1-math.exp(-STOCK)
Y=.25*F
AUT=Y-.05
BETA=.95
ARMS=('IQL_PUBLIC_COLD','PG_PUBLIC_COLD','IQL_PRIVATE_COLD','PG_PRIVATE_COLD',
      'IQL_PUBLIC_WARM','PG_PUBLIC_WARM')


@njit(cache=True)
def obs(h, i, signal, public):
    mask=h//3
    if mask==8:
        count=4
    elif public or i==3:
        count=(mask&1)+((mask>>1)&1)+((mask>>2)&1)
    else:
        count=(mask>>i)&1
    return (count*3+h%3)*2+signal


@njit(cache=True)
def sigmoid(x):
    return 1/(1+math.exp(-max(-20.,min(20.,x))))


@njit(cache=True)
def probability(q, theta, i, s, pay, pg, eps):
    if pg:
        p=sigmoid(theta[i,s,pay])
    else:
        difference=q[i,s,pay,1]-q[i,s,pay,0]
        p=1. if difference>0 else (0. if difference<0 else .5)
    return eps/2+(1-eps)*p


@njit(cache=True)
def material(actions, payments, good, losses):
    complete=actions[0]*actions[1]*actions[2]*actions[3]==1
    physical=np.full(4,AUT)
    if complete:
        for i in range(4):
            physical[i]=(Y+.8*F if good else -losses[i])-.05
    physical[3]-=.30*actions[3]
    reward=physical.copy()
    mask=0
    if complete and good:
        for i in range(3):
            reward[i]-=.25*payments[i]
            reward[3]+=.25*payments[i]
            mask+=payments[i]<<i
    return reward,physical,complete,mask


def initialize(groups, losses, arm):
    q=np.full((groups,4,30,2,2),AUT/.05)
    q[:,:,:,1,:]=BETA*AUT/.05
    theta=np.zeros((groups,4,30,2))
    baseline=np.full((groups,4,30,2),AUT/.05)
    baseline[:,:,:,1]=BETA*AUT/.05
    if arm.endswith('WARM'):
        for g in range(groups):
            for i in range(4):
                for s in range(30):
                    count=s//6; signal=s%2
                    cooperate=count in (2,3,4)
                    mode=int(cooperate and (losses[g,i]==1 or signal==1))
                    pay=int(cooperate and i<3 and losses[g,i]==1)
                    for head,choice in enumerate([mode,pay]):
                        q[g,i,s,head,choice]+=1.
                        theta[g,i,s,head]=math.log(19.)*(2*choice-1)
    return q,theta,baseline


@njit(cache=True)
def train_chunk(q, theta, baseline, h, lengths, buf_obs, buf_score, buf_reward,
                buf_physical, buf_pay, tape, losses, pg, public, start, total):
    groups=q.shape[0]
    counts=np.zeros(5,np.int64) # rounds, GOOD, BAD, actual payments, terminations
    for t in range(tape.shape[0]-1):
        eps=.20-.18*min(1.,(start+t)/(.8*total))
        for g in range(groups):
            good=tape[t,g,0]<.65
            signals=np.zeros(4,np.int64); states=np.zeros(4,np.int64)
            actions=np.zeros(4,np.int64); payments=np.zeros(3,np.int64)
            scores=np.zeros((4,2))
            for i in range(4):
                signals[i]=int((tape[t,g,1+i]<.8)==good)
                states[i]=obs(h[g],i,signals[i],public)
                p=probability(q[g],theta[g],i,states[i],0,pg,eps)
                actions[i]=int(tape[t,g,6+i]<p)
                if pg:
                    base=sigmoid(theta[g,i,states[i],0])
                    scores[i,0]=(actions[i]-p)/(p*(1-p))*(1-eps)*base*(1-base)
            reward,physical,complete,unused=material(actions,payments,good,losses[g])
            paying=complete and good
            if paying:
                for i in range(3):
                    p=probability(q[g],theta[g],i,states[i],1,pg,eps)
                    payments[i]=int(tape[t,g,10+i]<p)
                    if pg:
                        base=sigmoid(theta[g,i,states[i],1])
                        scores[i,1]=(payments[i]-p)/(p*(1-p))*(1-eps)*base*(1-base)
                reward,physical,complete,mask=material(actions,payments,good,losses[g])
                new_h=mask*3+2
            else:
                new_h=(h[g]//3)*3+int(complete and not good)
            done=tape[t,g,5]<.05
            next_h=24 if done else new_h
            if pg:
                k=lengths[g]
                assert k<buf_obs.shape[1], 'Relationship buffer exhausted; do not silently truncate.'
                for i in range(4):
                    buf_obs[g,k,i]=states[i]
                    buf_reward[g,k,i]=reward[i]
                    buf_physical[g,k,i]=physical[i]
                    for head in range(2):buf_score[g,k,i,head]=scores[i,head]
                buf_pay[g,k]=paying
                lengths[g]+=1
                if done:
                    gradients=np.zeros((4,30,2))
                    sums=np.zeros((4,30,2)); visits=np.zeros((4,30,2))
                    returns=np.zeros(4)
                    for j in range(lengths[g]-1,-1,-1):
                        for i in range(4):
                            returns[i]+=buf_reward[g,j,i]
                            s=buf_obs[g,j,i]
                            gradients[i,s,0]+=(returns[i]-baseline[g,i,s,0])*buf_score[g,j,i,0]
                            sums[i,s,0]+=returns[i]; visits[i,s,0]+=1
                            if i<3 and buf_pay[g,j]:
                                target=returns[i]-buf_physical[g,j,i]
                                gradients[i,s,1]+=(target-baseline[g,i,s,1])*buf_score[g,j,i,1]
                                sums[i,s,1]+=target; visits[i,s,1]+=1
                    for i in range(4):
                        for s in range(30):
                            for head in range(2):
                                theta[g,i,s,head]=max(-12.,min(12.,theta[g,i,s,head]+.02/20*gradients[i,s,head]))
                                if visits[i,s,head]:
                                    baseline[g,i,s,head]+=.05*(sums[i,s,head]/visits[i,s,head]-baseline[g,i,s,head])
                    lengths[g]=0
            else:
                next_values=np.zeros(4)
                next_good=tape[t+1,g,0]<.65
                for i in range(4):
                    next_signal=int((tape[t+1,g,1+i]<.8)==next_good)
                    s=obs(next_h,i,next_signal,public)
                    next_values[i]=0. if done else max(q[g,i,s,0,0],q[g,i,s,0,1])
                for i in range(4):
                    s=states[i]; a=actions[i]
                    q[g,i,s,0,a]+=.05*(reward[i]+next_values[i]-q[g,i,s,0,a])
                    if paying and i<3:
                        a=payments[i]
                        q[g,i,s,1,a]+=.05*(-.25*a+next_values[i]-q[g,i,s,1,a])
            h[g]=next_h
            counts[0]+=1; counts[1]+=paying; counts[2]+=complete and not good
            counts[3]+=payments.sum() if paying else 0; counts[4]+=done
    return counts


def root_seed(world):
    return int.from_bytes(hashlib.sha256(f'V202|ROOT|{world}'.encode()).digest()[:8],'little')


def probabilities(q,theta,pg):
    if pg:
        return 1/(1+np.exp(-theta))
    difference=q[...,1]-q[...,0]
    return np.where(difference>0,1.,np.where(difference<0,0.,.5))


def run_world(world,arm,steps=60000,groups=8,chunk=10000,destination=None):
    rng=np.random.Generator(np.random.Philox(root_seed(world)))
    losses=np.full((groups,4),7.)
    for g in range(groups):losses[g,:3]=rng.permutation([1.,1.,7.])
    q,theta,baseline=initialize(groups,losses,arm)
    pg=arm.startswith('PG'); public='_PUBLIC_' in arm
    h=np.full(groups,24,np.int64); lengths=np.zeros(groups,np.int64)
    buf_obs=np.zeros((groups,512,4),np.int64)
    buf_score=np.zeros((groups,512,4,2)); buf_reward=np.zeros((groups,512,4))
    buf_physical=np.zeros_like(buf_reward); buf_pay=np.zeros((groups,512),np.bool_)
    total_counts=np.zeros(5,np.int64); history=[]
    overlap=rng.random((1,groups,13))
    def save(step):
        if destination is None:return
        np.savez_compressed(destination/f'{arm}_world{world:02}_{step}.npz',
            q=q,theta=theta,baseline=baseline,losses=losses,h=h,lengths=lengths,
            buf_obs=buf_obs,buf_score=buf_score,buf_reward=buf_reward,
            buf_physical=buf_physical,buf_pay=buf_pay,overlap=overlap,
            step=step,total_counts=total_counts,history_json=json.dumps(history),
            RNG_state_json=json.dumps(rng.bit_generator.state,default=lambda x:x.tolist()))
    save(0)
    for start in range(0,steps,chunk):
        n=min(chunk,steps-start)
        tape=np.concatenate([overlap,rng.random((n,groups,13))],axis=0)
        overlap=tape[-1:].copy()
        counts=train_chunk(q,theta,baseline,h,lengths,buf_obs,buf_score,buf_reward,
            buf_physical,buf_pay,tape,losses,pg,public,start,steps)
        total_counts+=counts
        history.append(dict(step=start+n,counts=counts.tolist()))
        if destination is not None and start+n in (10000,30000,steps):
            save(start+n)
    p=probabilities(q,theta,pg)
    return dict(world=world,arm=arm,root_seed=root_seed(world),losses=losses,
                probabilities=p,counts=total_counts,history=history,
                ongoing_uncompleted_PG_relationships=int((lengths>0).sum()),
                uncompleted_PG_steps_not_used_for_update=int(lengths.sum()))
