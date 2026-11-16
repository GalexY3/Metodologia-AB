"""Execute the registered deterministic oracle flows, not additional world seeds."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from scipy.integrate import solve_ivp
from research_resource_limits import apply_limits
from v203_exact_gradient import initial,vector_field,gradients,history_spread,to_v202_probabilities
from v202_exact_evaluation import evaluate,deviation_audit

B=Path(__file__).resolve().parent
LOSS=np.array([1.,1.,7.,7.])
TIMES=np.unique(np.concatenate([[0.,60.,600.,6000.],np.geomspace(.1,6000,80)]))


def integrate(kind,natural,seed,rtol,atol):
    theta0=initial(kind,seed)
    calls=0
    def fun(t,x):
        nonlocal calls
        calls+=1
        assert calls<=200000,'Registered function-evaluation limit reached'
        eps=.20-.18*min(t/48,1.)
        return vector_field(x,natural,eps)
    solved=solve_ivp(fun,(0.,6000.),theta0.ravel(),method='RK45',t_eval=TIMES,rtol=rtol,atol=atol)
    assert solved.success,solved.message
    assert float(np.max(np.abs(solved.y)))<=12.001
    states=solved.y.T.reshape((-1,4,15,2,2))
    snapshots=[]
    for t in [0.,60.,600.,6000.]:
        ix=int(np.flatnonzero(solved.t==t)[0]);theta=states[ix]
        native=to_v202_probabilities(theta)
        eps=.20-.18*min(t/48,1.)
        gm,fi,adv,value,occ=gradients(theta,LOSS,eps)
        snapshots.append(dict(time=t,native_evaluation=evaluate(native,LOSS,True),
            public_deviations=deviation_audit(native,LOSS,True),
            behavior_normalized_private_return=(.05*value[12]).tolist(),
            mode_history_spread=history_spread(theta)[0],payment_history_spread=history_spread(theta)[1],
            exact_euclidean_gradient_norm=float(np.linalg.norm(gm)),
            discounted_occupancy=occ.tolist()))
    return solved.t,states,dict(kind=kind,natural=natural,seed=seed,rtol=rtol,atol=atol,
        success=True,field_evaluations=calls,snapshots=snapshots,
        final_mode_history_spread=history_spread(states[-1])[0],
        final_payment_history_spread=history_spread(states[-1])[1])


def main():
    registration=json.loads((B/'V203_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    assert registration['remote_bytes_verified_before_integration']
    for name,digest in registration['source_sha256'].items():
        assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    folder=B/'results/V203_EXACT_GRADIENT_FLOWS';folder.mkdir(exist_ok=False)
    (folder/'FREEZE.json').write_text(json.dumps(registration,indent=2),encoding='utf-8')
    cases=[('COLD',None),('WARM',None)]+[('JITTER',2031600+i) for i in range(8)]
    rows=[];clock=time.perf_counter()
    for kind,seed in cases:
        for natural in [False,True]:
            name=f'{kind}_{seed}_{"NPG" if natural else "EPG"}'
            try:
                times,states,row=integrate(kind,natural,seed,1e-8,1e-10)
                np.savez_compressed(folder/f'{name}.npz',times=times,logits=states)
                if kind in ['COLD','WARM']:
                    tt,ss,precise=integrate(kind,natural,seed,1e-9,1e-11)
                    np.savez_compressed(folder/f'{name}_PRECISION.npz',times=tt,logits=ss)
                    row['precision_run']=precise
                    difference=float(np.max(np.abs(to_v202_probabilities(states[-1])-to_v202_probabilities(ss[-1]))))
                    row['precision_native_probability_max_error']=difference
                    row['precision_endpoint_within_registered_tolerance']=bool(difference<=1e-4)
                rows.append(row)
                (folder/f'{name}.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
                print('V203',name,'functional',row['snapshots'][-1]['native_evaluation']['functional'],
                    'GOOD',row['snapshots'][-1]['native_evaluation']['discounted_GOOD_joint_rate'],
                    'calls',row['field_evaluations'],'elapsed',round(time.perf_counter()-clock,1),flush=True)
            except Exception as error:
                (folder/f'{name}_FAILED.json').write_text(json.dumps(dict(kind=kind,natural=natural,seed=seed,
                    error=repr(error)),indent=2),encoding='utf-8')
                raise
    summary=dict(study='V203',oracle_not_private_learner=True,deterministic_sensitivity_cases=20,
        additional_precision_runs=4,rows=rows,original_V202_H1='FAIL',
        independent_external_confirmation=False,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (folder/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V203_DONE',flush=True)


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
