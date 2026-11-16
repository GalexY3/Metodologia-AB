"""Pre-integration checks against the independent V202 27-state evaluator."""
from pathlib import Path
import json
import numpy as np
from research_resource_limits import apply_limits
from v203_exact_gradient import model,gradients,vector_field,to_v202_probabilities,initial
from v202_exact_evaluation import operator

B=Path(__file__).resolve().parent
LOSS=np.array([1.,1.,7.,7.])


def independent_value(theta):
    p=to_v202_probabilities(theta)
    tr,r,_,_=operator(p,LOSS,True)
    return np.linalg.solve(np.eye(27)-.95*tr,r)[24]*.05


def main():
    output=B/'results/V203_PRE_INTEGRATION_AUDIT.json';assert not output.exists()
    rng=np.random.Generator(np.random.Philox(20320261116))
    maximum_value=0.;maximum_gradient=0.;checks=0
    for repeat in range(3):
        theta=rng.normal(0,.7,(4,15,2,2))
        grad,fisher,adv,values,occupancy=gradients(theta,LOSS)
        independent=independent_value(theta)
        error=float(np.max(np.abs(independent-.05*values[12])))
        maximum_value=max(maximum_value,error);assert error<1e-12
        assert np.min(fisher)>=0 and abs(occupancy.sum()-1)<1e-12
        assert np.max(np.abs(grad[:,14]))<1e-14
        assert np.max(np.abs(grad[3,:,:,1]))==0.
        for i in range(4):
            for h in range(15):
                for s in range(2):
                    for head in range(2):
                        delta=np.zeros_like(theta);delta[i,h,s,head]=1e-5
                        fd=(independent_value(theta+delta)[i]-independent_value(theta-delta)[i])/2e-5
                        err=abs(fd-grad[i,h,s,head]);maximum_gradient=max(maximum_gradient,err)
                        assert err<1e-8,(i,h,s,head,fd,grad[i,h,s,head])
                        checks+=1
    invariance=[]
    for repeat in range(4):
        private_logits=np.zeros((4,1,2,2)) if repeat==0 else rng.normal(0,.7,(4,1,2,2))
        theta=np.broadcast_to(private_logits,(4,15,2,2)).copy()
        natural=vector_field(theta.ravel(),True).reshape(theta.shape)
        ordinary=vector_field(theta.ravel(),False).reshape(theta.shape)
        mode=float(np.max(np.ptp(natural[:,:14,:,0],axis=1)))
        pay=float(np.max(np.ptp(natural[:3,:14,:,1],axis=1)))
        assert max(mode,pay)<1e-9
        ordinary_spread=float(np.max(np.ptp(ordinary[:,:14,:,0],axis=1)))
        assert ordinary_spread>1e-5
        invariance.append(dict(case=repeat,natural_mode_spread=mode,natural_pay_spread=pay,
                               ordinary_mode_spread=ordinary_spread))
    g,f,a,v,d=gradients(initial('COLD'),LOSS)
    assert np.max(np.abs(a[:3,:14,:,1]+.25))<1e-12
    assert a[3,12,1,0]<0 and a[3,12,0,0]<0
    result=dict(status='PASS',independent_27_vs_15_state_value_checks=3,
        maximum_value_error=maximum_value,finite_difference_parameters=checks,
        maximum_private_gradient_error=maximum_gradient,
        history_independent_vector_field_checks=invariance,
        cold_conditional_payment_advantage=-.25,
        cold_critical_JOINT_minus_AUTO=[float(a[3,12,s,0]) for s in [0,1]],
        oracle_model_and_peer_policy_access=True,private_realized_feedback_learner=False,
        new_scientific_integrations_executed=False)
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
