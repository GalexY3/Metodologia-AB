"""Technical checks before registration; no scientific endpoints selected here."""
from pathlib import Path
import json
import math
import numpy as np
from research_resource_limits import apply_limits
from v202_relational_learning import initialize,probabilities,obs,run_world,AUT,F,Y
from v202_exact_evaluation import operator,enumerate_operator_row,evaluate,deviation_audit

B=Path(__file__).resolve().parent


def main():
    destination=B/'results/V202_PRE_RUN_TECHNICAL_AUDIT.json'
    assert not destination.exists()
    rng=np.random.default_rng(2026111602)
    loss=np.array([1.,1.,7.,7.]); maximum=0.; checks=0
    for public in [False,True]:
        for repeat in range(3):
            p=rng.uniform(.03,.97,(4,30,2))
            t,r,_,_=operator(p,loss,public)
            for h in [0,2,5,11,23,24,25,26]:
                tt,rr=enumerate_operator_row(p,loss,public,h)
                error=max(np.max(np.abs(t[h]-tt)),np.max(np.abs(r[h]-rr)))
                assert error<1e-12
                maximum=max(maximum,float(error));checks+=1
    # Private ordinary sees own last successful payment, not others' count.
    privacy_checks=0
    for i in range(3):
        for a in range(8):
            for b in range(8):
                if ((a>>i)&1)==((b>>i)&1):
                    assert obs(a*3+2,i,1,False)==obs(b*3+2,i,1,False)
                    privacy_checks+=1
    assert obs(1*3+2,3,1,False)!=obs(3*3+2,3,1,False)
    # Mixture-policy score derivative, not a gradient of a different policy.
    max_gradient_error=0.
    for theta in rng.uniform(-5,5,100):
        for eps in [.02,.20]:
            b=1/(1+math.exp(-theta));p=eps/2+(1-eps)*b
            for action in [0,1]:
                exact=(action-p)/(p*(1-p))*(1-eps)*b*(1-b)
                def logp(x):
                    v=eps/2+(1-eps)/(1+math.exp(-x))
                    return math.log(v if action else 1-v)
                numerical=(logp(theta+1e-5)-logp(theta-1e-5))/2e-5
                error=abs(exact-numerical);max_gradient_error=max(max_gradient_error,error)
                assert error<1e-7
    q,theta,base=initialize(1,loss[None,:],'IQL_PUBLIC_WARM')
    oracle=probabilities(q,theta,False)[0]
    evaluated=evaluate(oracle,loss,True)
    br=deviation_audit(oracle,loss,True)
    assert abs(evaluated['discounted_GOOD_joint_rate']-.416)<1e-12
    assert evaluated['functional']
    assert br['max_normalized_gain']<1e-10
    physical=.416*.8*F-.014*(Y+loss)
    physical[:2]-=.416*.25;physical[3]+=.416*.5-.177
    assert np.max(np.abs(np.array(evaluated['gain_over_autarky'])-physical))<1e-12
    # The first GOOD opportunity arrives geometrically, not certainly at t=0.
    first_good_normalized=.05*.416/(1-.95*(1-.416))
    assert abs(evaluated['disabled_payment_GOOD_rate']-first_good_normalized)<1e-12
    assert abs(evaluated['payment_disable_effect']-(.416-first_good_normalized))<1e-12
    # Tiny separate debug seed range, only finite execution/shape assertions.
    smoke=[]
    for arm in ['IQL_PUBLIC_COLD','PG_PUBLIC_COLD','IQL_PRIVATE_COLD','PG_PRIVATE_COLD']:
        item=run_world(90000,arm,steps=200,groups=2,chunk=100)
        assert item['probabilities'].shape==(2,4,30,2)
        assert np.isfinite(item['probabilities']).all()
        smoke.append(dict(arm=arm,finite=True,round_count=int(item['counts'][0])))
    result=dict(status='PASS',conditional_factorization_rows=checks,max_scalar_error=maximum,
        ordinary_privacy_invariance_checks=privacy_checks,mixture_gradient_checks=400,
        max_finite_difference_error=max_gradient_error,
        frozen_programmed_certificate=evaluated,public_best_response_certificate=br,
        geometric_termination_probability=.05,learning_discount_in_updates=1.,
        resulting_valuation_discount=.95,no_double_discount=True,
        smoke=smoke,smoke_is_not_scientific_evidence=True)
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
