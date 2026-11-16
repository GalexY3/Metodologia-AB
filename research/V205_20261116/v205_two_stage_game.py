"""Literal two-stage game and known AA fields, independent of V202--V204.

The hypothetical counterexample is an audit of a published method, not an
institution learned here. Each player has a separate normalized policy.
"""
import itertools
import numpy as np


def sigmoid(theta):return 1/(1+np.exp(-np.asarray(theta)))


def state_values(p,gamma,coupling=0.):
    v=np.zeros((2,3),dtype=np.result_type(p,float))
    for h,z in [(1,1),(2,-1)]:
        f=2*p[0,h]-1;g=2*p[1,h]-1
        v[0,h]=coupling*f*g
        v[1,h]=f*(z-coupling*g)
    x=2*p[0,0]-1;zbar=2*p[1,0]-1
    v[0,0]=zbar*(1+coupling*x)+gamma*(p[1,0]*v[0,1]+(1-p[1,0])*v[0,2])
    v[1,0]=-coupling*x*zbar+gamma*(p[1,0]*v[1,1]+(1-p[1,0])*v[1,2])
    return v


def trajectories(p,gamma=.9,advantages='joint',lmbda=.95,coupling=0.):
    """Enumerate all 16 joint action paths; no samples or fitted critic."""
    v=state_values(p,gamma,coupling)
    for a0,b0,a1,b1 in itertools.product([0,1],repeat=4):
        z=2*b0-1;state=1 if b0 else 2
        mass=1.
        actions=np.array([[a0,a1],[b0,b1]])
        for i in range(2):
            for t,h in enumerate([0,state]):
                prob=p[i,h];mass*=prob if actions[i,t] else 1-prob
        x=2*a0-1;f=2*a1-1;g=2*b1-1
        rewards=np.array([[z*(1+coupling*x),coupling*f*g],[-coupling*x*z,f*(z-coupling*g)]])
        q=rewards.copy();q[:,0]+=gamma*v[:,state]
        adv=q-v[:,[0,state]]
        if advantages=='marginal':
            xb=2*p[0,0]-1;zb=2*p[1,0]-1;fb=2*p[0,state]-1;gb=2*p[1,state]-1
            adv=np.array([[coupling*zb*(x-xb),coupling*gb*(f-fb)],
                [-coupling*xb*z+gamma*v[1,state]-v[1,0],-coupling*fb*(g-gb)]])
        elif advantages=='gae':
            adv=adv.copy();adv[:,0]+=gamma*lmbda*adv[:,1]
        elif advantages!='joint':raise ValueError(advantages)
        scores=np.zeros((2,2,3))
        for i in range(2):
            for t,h in enumerate([0,state]):scores[i,t,h]=actions[i,t]-p[i,h]
        yield dict(actions=actions,states=[0,state],mass=mass,rewards=rewards,
                   advantages=adv,scores=scores,z=z)


def returns_p(p,gamma=.9,coupling=0.):
    result=np.zeros(2)
    for path in trajectories(p,gamma,coupling=coupling):
        result+=path['mass']*(path['rewards']@np.array([1.,gamma]))
    return result


def best_responses_p(p,gamma=.9,coupling=0.):
    value=returns_p(p,gamma,coupling);gains=[];choices=[];max_values=[]
    for i in range(2):
        alternatives=[]
        for policy in itertools.product([0.,1.],repeat=3):
            changed=p.copy();changed[i]=policy
            alternatives.append((float(returns_p(changed,gamma,coupling)[i]),policy))
        best=max(alternatives,key=lambda x:x[0]);max_values.append(best[0])
        gains.append(best[0]-float(value[i]));choices.append(best[1])
    return dict(values=value.tolist(),best_response_values=max_values,
        gains=gains,max_gain=max(gains),best_deterministic_policies=choices,
        policies_per_player=8)


def aa_field(theta,gamma=.9,beta=.3,variant='eq8',advantages='joint',lmbda=.95,coupling=0.):
    p=sigmoid(theta);own=np.zeros_like(p);extra=np.zeros_like(p)
    for path in trajectories(p,gamma,advantages,lmbda,coupling):
        a=path['advantages'];score=path['scores'];prob=path['mass']
        for i in range(2):
            j=1-i
            for t in range(2):
                own[i]+=prob*gamma**t*a[i,t]*score[i,t]
                if variant=='eq8':
                    past=sum(gamma**(t-k)*a[i,k] for k in range(t))
                    weight=gamma**(t+1)
                elif variant=='eq59':
                    past=sum(a[i,k] for k in range(t));weight=1/(1+t)
                else:raise ValueError(variant)
                extra[i]+=prob*weight*past*a[j,t]*score[i,t]
    return own+beta*extra,own,extra
