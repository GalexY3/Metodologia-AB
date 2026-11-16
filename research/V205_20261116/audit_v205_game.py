"""Technical game/value/score checks away from the primary equilibrium."""
from pathlib import Path
import hashlib
import json
import numpy as np
from v205_two_stage_game import sigmoid,trajectories,returns_p,state_values

B=Path(__file__).resolve().parent


def main():
    rng=np.random.Generator(np.random.Philox(2051900));max_value=0.;max_gradient=0.;rows=[]
    for case in range(4):
        theta=rng.normal(0,.6,(2,3));p=sigmoid(theta);gamma=[.3,.5,.9,.99][case]
        coupling=[0.,.1,.3,1.][case]
        paths=list(trajectories(p,gamma,coupling=coupling));mass=sum(x['mass'] for x in paths)
        val=returns_p(p,gamma,coupling);analytic=state_values(p,gamma,coupling)[:,0]
        max_value=max(max_value,float(np.max(np.abs(val-analytic))))
        score=np.zeros((2,2,3))
        for path in paths:
            ret=path['rewards']@np.array([1.,gamma])
            for i in range(2):score[i]+=path['mass']*ret[i]*path['scores'].sum(1)
        for k in range(theta.size):
            plus=theta.copy();minus=theta.copy();plus.ravel()[k]+=1e-5;minus.ravel()[k]-=1e-5
            fd=(returns_p(sigmoid(plus),gamma,coupling)-returns_p(sigmoid(minus),gamma,coupling))/(2e-5)
            max_gradient=max(max_gradient,float(np.max(np.abs(fd-score.reshape((2,-1))[:,k]))))
        assert abs(mass-1)<1e-12
        rows.append(dict(case=case,gamma=gamma,coupling=coupling,mass=mass,value_error=float(np.max(np.abs(val-analytic)))))
    assert max_value<1e-12 and max_gradient<1e-8
    result=dict(status='PASS',stage='TECHNICAL_GAME_QA_NOT_PRIMARY_AA_TEST',
        cases=4,scalar_first_derivative_checks=48,max_value_error=max_value,max_gradient_error=max_gradient,
        primary_equilibrium_AA_field_not_executed=True,rows=rows,
        sources={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in ['v205_two_stage_game.py','audit_v205_game.py']})
    out=B/'results/V205_TECHNICAL_GAME_AUDIT_EXPANDED.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
