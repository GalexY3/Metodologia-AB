"""Validate the exact exploration-mixture gradient used by the flow control."""
from pathlib import Path
import json
import numpy as np
from research_resource_limits import apply_limits
from v203_exact_gradient import probability,gradients,vector_field
from v202_exact_evaluation import operator

B=Path(__file__).resolve().parent
LOSS=np.array([1.,1.,7.,7.])


def objective(theta,epsilon):
    p=(epsilon/2+(1-epsilon)*probability(theta)).reshape(4,30,2)
    transition,reward,_,_=operator(p,LOSS,True)
    return .05*np.linalg.solve(np.eye(27)-.95*transition,reward)[24]


def main():
    output=B/'results/V203_MIXTURE_GRADIENT_AUDIT.json';assert not output.exists()
    rng=np.random.Generator(np.random.Philox(20311602));rows=[]
    for epsilon in [0.,.02,.20]:
        theta=rng.normal(0,.7,(4,15,2,2))
        gradient,fisher,adv,value,d=gradients(theta,LOSS,epsilon)
        maximum=0.;checks=0
        for index in np.ndindex(theta.shape):
            delta=np.zeros_like(theta);delta[index]=1e-5
            numerical=(objective(theta+delta,epsilon)[index[0]]-objective(theta-delta,epsilon)[index[0]])/2e-5
            error=abs(numerical-gradient[index]);maximum=max(maximum,error)
            assert error<1e-8,(epsilon,index,error)
            checks+=1
        constant=np.broadcast_to(rng.normal(0,.7,(4,1,2,2)),theta.shape).copy()
        natural=vector_field(constant.ravel(),True,epsilon).reshape(theta.shape)
        mode=float(np.max(np.ptp(natural[:,:14,:,0],axis=1)))
        pay=float(np.max(np.ptp(natural[:3,:14,:,1],axis=1)))
        assert max(mode,pay)<1e-9
        rows.append(dict(epsilon=epsilon,finite_differences=checks,max_error=maximum,
                         natural_history_mode_spread=mode,natural_history_pay_spread=pay))
    result=dict(status='PASS',current_mixture_gradient=True,total_finite_differences=720,rows=rows,
        exact_gradient_for_frozen_instantaneous_epsilon=True,
        not_a_full_derivative_of_future_learning_or_future_exploration_schedule=True)
    output.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
