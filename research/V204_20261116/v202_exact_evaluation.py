"""Exact frozen-policy Markov evaluation; no trajectories counted as replicates."""
import itertools
import numpy as np
from v202_relational_learning import obs,AUT,F,Y,BETA

START=24


def components(p,h,public):
    pm=np.array([[p[i,obs(h,i,s,public),0] for s in [0,1]] for i in range(4)])
    pp=np.array([[p[i,obs(h,i,s,public),1] for s in [0,1]] for i in range(3)])
    qg=pm@np.array([.2,.8]); qb=pm@np.array([.8,.2])
    numerator=(pm[:3]*pp)@np.array([.2,.8])
    pay=np.divide(numerator,qg[:3],out=np.zeros(3),where=qg[:3]>0)
    return pm,qg,qb,pay


def mask_distribution(pay):
    out=np.ones(8)
    for mask in range(8):
        for i in range(3):out[mask]*=pay[i] if (mask>>i)&1 else 1-pay[i]
    return out


def operator(p,losses,public,no_payments=False):
    transition=np.zeros((27,27)); reward=np.full((27,4),AUT)
    good=np.zeros(27); paid=np.zeros((27,3))
    for h in range(27):
        pm,qg,qb,pay=components(p,h,public)
        if no_payments:pay[:]=0.
        pg=.65*np.prod(qg); pb=.35*np.prod(qb)
        transition[h,(h//3)*3]+=max(0.,1-pg-pb)
        transition[h,(h//3)*3+1]+=pb
        distribution=mask_distribution(pay)
        for mask in range(8):transition[h,mask*3+2]+=pg*distribution[mask]
        reward[h]+=.8*F*pg-(Y+losses)*pb
        reward[h,3]-=.3*(.65*qg[3]+.35*qb[3])
        reward[h,:3]-=.25*pg*pay; reward[h,3]+=.25*pg*pay.sum()
        good[h]=pg; paid[h]=pg*pay
    assert np.max(np.abs(transition.sum(1)-1))<1e-12
    return transition,reward,good,paid


def evaluate(p,losses,public):
    transition,reward,good,paid=operator(p,losses,public)
    system=np.eye(27)-BETA*transition
    values=np.linalg.solve(system,reward)
    good_values=np.linalg.solve(system,good)
    aut_transition,aut_reward,aut_good,_=operator(p,losses,public,True)
    no_pay_good=np.linalg.solve(np.eye(27)-BETA*aut_transition,aut_good)
    native=(1-BETA)*values[START]
    rate=(1-BETA)*good_values[START]
    ablated=(1-BETA)*no_pay_good[START]
    payment_rates=(1-BETA)*np.linalg.solve(system,paid)[START]
    # One forced omission at a successful opportunity, not a permanent ban.
    _,_,_,conditional_pay=components(p,START,public)
    distribution=mask_distribution(conditional_pay)
    default_responses=[]
    for i in range(3):
        difference=sum(distribution[m]*(good_values[m*3+2]-good_values[(m&~(1<<i))*3+2])
                       for m in range(8))*(1-BETA)
        default_responses.append(float(difference))
    return dict(normalized_private_return=native.tolist(),gain_over_autarky=(native-AUT).tolist(),
        discounted_GOOD_joint_rate=float(rate),disabled_payment_GOOD_rate=float(ablated),
        payment_disable_effect=float(rate-ablated),normalized_payments_per_donor=payment_rates.tolist(),
        single_default_future_GOOD_effect_at_START=default_responses,
        functional=bool(np.min(native-AUT)>=.02 and rate>=.20 and rate-ablated>=.10),
        exact_value_residual=float(np.max(np.abs(system@values-reward))))


def public_best_response(p,losses,i):
    """Own signal observed before mode; own payment chosen after GOOD completion."""
    r=np.zeros((27,2,3)); tr=np.zeros((27,2,3,27))
    for h in range(27):
        pm,qg,qb,pay=components(p,h,True)
        others=[j for j in range(4) if j!=i]
        for s,posterior in [(0,13/41),(1,52/59)]:
            pg=posterior*np.prod(qg[others]); pb=(1-posterior)*np.prod(qb[others])
            r[h,s,0]=AUT;tr[h,s,0,(h//3)*3]=1.
            for a in [0,1]:
                x=pay.copy()
                if i<3:x[i]=a
                net=-.25*a if i<3 else .25*x.sum()
                r[h,s,1+a]=AUT-.3*(i==3)+pg*(.8*F+net)-pb*(Y+losses[i])
                tr[h,s,1+a,(h//3)*3]=max(0.,1-pg-pb)
                tr[h,s,1+a,(h//3)*3+1]=pb
                dist=mask_distribution(x)
                for mask in range(8):tr[h,s,1+a,mask*3+2]+=pg*dist[mask]
    value=np.full(27,AUT/.05)
    for it in range(100):
        q=r+BETA*np.einsum('hsan,n->hsa',tr,value)
        choice=q.argmax(2)
        rr=np.zeros(27);tt=np.zeros((27,27))
        for s,weight in [(0,.41),(1,.59)]:
            rr+=weight*r[np.arange(27),s,choice[:,s]]
            tt+=weight*tr[np.arange(27),s,choice[:,s]]
        updated=np.linalg.solve(np.eye(27)-BETA*tt,rr)
        diff=np.max(np.abs(updated-value));value=updated
        if diff<1e-10:break
    q=r+BETA*np.einsum('hsan,n->hsa',tr,value)
    residual=float(np.max(np.abs((q.max(2)@np.array([.41,.59]))-value)))
    assert residual<1e-8,(residual,it)
    # Full bitmask does not provide extra information when all other public
    # policies only depend on count and last outcome.
    max_equivalence=0.
    for outcome in range(3):
        for count in range(4):
            indices=[m*3+outcome for m in range(8) if m.bit_count()==count]
            max_equivalence=max(max_equivalence,float(np.ptp(value[indices])))
    assert max_equivalence<1e-9
    return value,dict(iterations=it+1,residual=residual,equal_public_count_value_error=max_equivalence)


def deviation_audit(p,losses,public):
    transition,reward,_,_=operator(p,losses,public)
    value=np.linalg.solve(np.eye(27)-BETA*transition,reward)
    gains=[];details=[]
    if public:
        for i in range(4):
            br,check=public_best_response(p,losses,i)
            gains.append(float((1-BETA)*(br[START]-value[START,i])))
            details.append(check)
        return dict(scope='Exact public-information best response, including optimal conditional payment',
                    normalized_gain_per_agent=gains,max_normalized_gain=max(gains),checks=details)
    for i in range(4):
        candidates=[]
        for kind in ['AUTO_ALWAYS','JOINT_ALWAYS','FOLLOW_SIGNAL','NEVER_PAY']:
            changed=p.copy()
            if kind=='NEVER_PAY':changed[i,:,1]=0.
            elif kind=='FOLLOW_SIGNAL':changed[i,:,0]=np.arange(30)%2
            else:changed[i,:,0]=int(kind=='JOINT_ALWAYS')
            t,r,_,_=operator(changed,losses,False)
            altered=np.linalg.solve(np.eye(27)-BETA*t,r[:,i])
            candidates.append(dict(deviation=kind,normalized_gain=float((1-BETA)*(altered[START]-value[START,i]))))
        gains.append(max(0.,max(c['normalized_gain'] for c in candidates)));details.append(candidates)
    return dict(scope='Feasible own-information deviations only; lower bound, NOT an optimal POMDP best response or equilibrium certificate',
                normalized_gain_per_agent=gains,max_normalized_gain=max(gains),checks=details)


def enumerate_operator_row(p,losses,public,h):
    """Independent literal enumeration, avoids the conditional-factor formula."""
    transition=np.zeros(27);reward=np.zeros(4)
    for good,prior in [(False,.35),(True,.65)]:
        for signals in itertools.product([0,1],repeat=4):
            probability=prior
            for s in signals:probability*=((.8 if s else .2) if good else (.2 if s else .8))
            for actions in itertools.product([0,1],repeat=4):
                prob=probability
                for i,a in enumerate(actions):
                    x=p[i,obs(h,i,signals[i],public),0];prob*=x if a else 1-x
                if all(actions) and good:
                    payment_vectors=itertools.product([0,1],repeat=3)
                else:payment_vectors=[(0,0,0)]
                for payment in payment_vectors:
                    pr=prob
                    if all(actions) and good:
                        for i,a in enumerate(payment):
                            x=p[i,obs(h,i,signals[i],public),1];pr*=x if a else 1-x
                    physical=np.full(4,AUT)
                    if all(actions):physical=np.array([(Y+.8*F if good else -losses[i])-.05 for i in range(4)])
                    physical[3]-=.3*actions[3]
                    if all(actions) and good:
                        for i,a in enumerate(payment):physical[i]-=.25*a;physical[3]+=.25*a
                        new=sum(payment[i]<<i for i in range(3))*3+2
                    else:new=(h//3)*3+int(all(actions) and not good)
                    transition[new]+=pr;reward+=pr*physical
    return transition,reward
