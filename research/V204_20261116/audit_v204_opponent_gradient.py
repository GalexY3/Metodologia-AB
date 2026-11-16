"""Technical checks on three arbitrary policies; no learning trajectories."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import torch
from v204_opponent_gradient import values,all_gradients,lola_components,field
from v203_exact_gradient import gradients,to_v202_probabilities
from v202_exact_evaluation import operator
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
LOSS=np.array([1.,1.,7.,7.])


def independent_values(theta,epsilon):
    native=to_v202_probabilities(theta)
    p=epsilon/2+(1-epsilon)*native
    t,r,_,_=operator(p,LOSS,True)
    return .05*np.linalg.solve(np.eye(27)-.95*t,r)[24]


def main():
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    rng=np.random.Generator(np.random.Philox(2041600))
    records=[];clock=time.perf_counter()
    max_val=0;max_grad=0;max_hvp=0;max_own=0
    for case,eps in enumerate([0.,.02,.20]):
        theta=rng.normal(0,.7,(4,15,2,2))
        x=torch.tensor(theta,dtype=torch.float64,requires_grad=True)
        u,g=all_gradients(x,epsilon=eps)
        gg=g.detach().numpy();vv=u.detach().numpy()
        max_val=max(max_val,float(np.max(np.abs(vv-independent_values(theta,eps)))))
        ng=gradients(theta,LOSS,eps)[0]
        max_own=max(max_own,float(np.max(np.abs(np.stack([gg[i,i] for i in range(4)])-ng))))
        step=1e-5;local=0
        for k in range(theta.size):
            plus=theta.copy();minus=theta.copy();plus.ravel()[k]+=step;minus.ravel()[k]-=step
            fd=(independent_values(plus,eps)-independent_values(minus,eps))/(2*step)
            error=float(np.max(np.abs(fd-gg.reshape((4,-1))[:,k])))
            local=max(local,error)
        max_grad=max(max_grad,local)
        hvp_errors=[]
        for i in range(4):
            for j in range(4):
                if i==j:continue
                direction=rng.choice(np.array([-1.,1.]),size=(15,2,2))/np.sqrt(60.)
                vector=gg[i,j].copy()
                term=(g[j,j]*torch.tensor(vector,dtype=torch.float64)).sum()
                analytic=torch.autograd.grad(term,x,retain_graph=True)[0][i].detach().numpy()
                plus=theta.copy();minus=theta.copy();plus[i]+=1e-4*direction;minus[i]-=1e-4*direction
                gp=gradients(plus,LOSS,eps)[0][j];gm=gradients(minus,LOSS,eps)[0][j]
                fd=float(np.sum((gp-gm)*vector)/(2e-4))
                exact=float(np.sum(analytic*direction))
                hvp_errors.append(abs(fd-exact))
        max_hvp=max(max_hvp,max(hvp_errors))
        records.append(dict(case=case,epsilon=eps,scalar_gradient_checks=960,
            maximum_gradient_error=local,bilinear_hessian_checks=12,maximum_hessian_error=max(hvp_errors)))
        print('V204_TECHNICAL',case,eps,local,max(hvp_errors),flush=True)
    assert max_val<1e-11 and max_own<1e-11 and max_grad<1e-8 and max_hvp<1e-8
    # Equation (4.4) identity at a technical point, including eta=0 control.
    x=torch.tensor(theta,dtype=torch.float64,requires_grad=True)
    _,own,correction=lola_components(x,epsilon=.2)
    z=field(theta.ravel(),eta=0.,epsilon=.2)
    assert np.max(np.abs(z-own.detach().numpy().ravel()))<1e-13
    start=time.perf_counter()
    for _ in range(5):field(theta.ravel(),eta=1.,epsilon=.2)
    result=dict(status='PASS',study='V204_TECHNICAL_ONLY',scientific_learning_trajectories_executed=False,
        arbitrary_debug_seed=2041600,scalar_first_derivative_checks=2880,bilinear_hessian_checks=36,
        maximum_value_error=max_val,maximum_own_gradient_error=max_own,
        maximum_cross_gradient_error=max_grad,maximum_hessian_bilinear_error=max_hvp,
        mean_LOLA_field_seconds=(time.perf_counter()-start)/5,elapsed_seconds=time.perf_counter()-clock,
        original_method='LOLA-Ex Eq. 4.4; G[i,j] multiplier stopped in correction',
        original_contribution=False,model_and_peer_policy_oracle=True,private_realized_feedback=False,
        full_monetary_given_cost_in_every_private_return=True,
        sources={n:hashlib.sha256((B/n).read_bytes()).hexdigest() for n in ['v204_opponent_gradient.py','audit_v204_opponent_gradient.py']},
        records=records,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    out=B/'results/V204_PRE_TRAJECTORY_TECHNICAL_AUDIT.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
