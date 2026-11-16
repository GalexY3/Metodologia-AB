"""Execute only the frozen exact LOLA rival. No rate or architecture sweep."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import torch
from scipy.integrate import solve_ivp
from research_resource_limits import apply_limits
from v204_opponent_gradient import field
from v203_exact_gradient import initial,model,to_v202_probabilities,history_spread
from v202_exact_evaluation import evaluate,deviation_audit

B=Path(__file__).resolve().parent
LOSS=np.array([1.,1.,7.,7.])
TIMES=np.unique(np.concatenate([[0.,60.,600.,6000.],np.geomspace(.1,6000,80)]))


class IntegrationFailure(RuntimeError):
    def __init__(self,error,calls,last_t,last_x):
        super().__init__(str(error))
        self.calls=calls;self.last_t=last_t;self.last_x=last_x.copy()


def integrate(kind,seed,rtol,atol):
    calls=0;last_t=0.;last_x=initial(kind,seed).ravel()
    def fun(t,x):
        nonlocal calls,last_t,last_x
        calls+=1
        last_t=t;last_x=x.copy()
        if calls>5000:raise RuntimeError('Registered field-evaluation cap reached')
        if calls%250==0:print('V204_RHS',kind,seed,'calls',calls,'t',round(t,4),flush=True)
        eps=.20-.18*min(t/48,1.)
        clipped=np.clip(x,-12.,12.)
        f=field(clipped,eta=20.,epsilon=eps,lola=True)
        f[((x>=12)&(f>0))|((x<=-12)&(f<0))]=0.
        return f
    try:
        solved=solve_ivp(fun,(0.,6000.),initial(kind,seed).ravel(),method='RK45',
            t_eval=TIMES,rtol=rtol,atol=atol)
    except Exception as error:
        raise IntegrationFailure(error,calls,last_t,last_x) from error
    if not solved.success:raise RuntimeError(solved.message)
    if float(np.max(np.abs(solved.y)))>12.001:raise RuntimeError('Registered logit-overshoot margin exceeded')
    states=solved.y.T.reshape((-1,4,15,2,2))
    snaps=[]
    for t in [0.,60.,600.,6000.]:
        ix=int(np.flatnonzero(solved.t==t)[0]);theta=states[ix];p=to_v202_probabilities(theta)
        eps=.20-.18*min(t/48,1.)
        value=model(theta,LOSS,eps)[3]
        e=evaluate(p,LOSS,True);br=deviation_audit(p,LOSS,True)
        snaps.append(dict(time=t,native_evaluation=e,public_deviations=br,
            stable_functional=bool(e['functional'] and br['max_normalized_gain']<=.01),
            behavior_normalized_private_return=(.05*value[12]).tolist(),
            mode_history_spread=history_spread(theta)[0],payment_history_spread=history_spread(theta)[1]))
    return solved.t,states,dict(status='SUCCESS',kind=kind,seed=seed,method='LOLA_EX_EQ4_4',
        eta=20.,rtol=rtol,atol=atol,field_evaluations=calls,snapshots=snaps)


def main():
    receipt=json.loads((B/'V204_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['remote_bytes_verified_before_integration']
    for name,digest in receipt['source_sha256'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    folder=B/'results/V204_LOLA_NET_RETURN';folder.mkdir(exist_ok=False)
    (folder/'FREEZE.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    cases=[('COLD',None),('WARM',None)]+[('JITTER',2031600+i) for i in range(8)]
    rows=[];clock=time.perf_counter()
    for kind,seed in cases:
        stem=f'{kind}_{seed}_LOLA';print('V204_START',stem,flush=True)
        try:
            times,states,row=integrate(kind,seed,1e-8,1e-10)
            np.savez_compressed(folder/f'{stem}.npz',times=times,logits=states)
            if kind in ['COLD','WARM']:
                try:
                    tt,ss,precise=integrate(kind,seed,1e-9,1e-11)
                    np.savez_compressed(folder/f'{stem}_PRECISION.npz',times=tt,logits=ss)
                    row['precision_run']=precise
                    error=float(np.max(np.abs(to_v202_probabilities(states[-1])-to_v202_probabilities(ss[-1]))))
                    row['precision_native_probability_max_error']=error
                    row['precision_endpoint_within_registered_tolerance']=bool(error<=1e-4)
                except Exception as error:
                    row['precision_run']=dict(status='FAILED',error=repr(error))
                    row['precision_endpoint_within_registered_tolerance']=False
                    if isinstance(error,IntegrationFailure):
                        np.savez_compressed(folder/f'{stem}_PRECISION_FAILED_LAST_RHS.npz',
                            time=error.last_t,logits=error.last_x,field_evaluations=error.calls)
            print('V204_END',stem,'functional',row['snapshots'][-1]['native_evaluation']['functional'],
                'stable',row['snapshots'][-1]['stable_functional'],'GOOD',row['snapshots'][-1]['native_evaluation']['discounted_GOOD_joint_rate'],
                'calls',row['field_evaluations'],'elapsed',round(time.perf_counter()-clock,1),flush=True)
        except Exception as error:
            row=dict(status='FAILED_NO_VALID_ENDPOINT',kind=kind,seed=seed,method='LOLA_EX_EQ4_4',error=repr(error))
            if isinstance(error,IntegrationFailure):
                row.update(field_evaluations=error.calls,last_RHS_time=error.last_t,
                    last_RHS_argument_not_accepted_solver_checkpoint=True)
                np.savez_compressed(folder/f'{stem}_FAILED_LAST_RHS.npz',
                    time=error.last_t,logits=error.last_x,field_evaluations=error.calls)
            print('V204_FAILED',stem,repr(error),flush=True)
        rows.append(row);(folder/f'{stem}.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
    cold=rows[0];jitter=[r for r in rows if r['kind']=='JITTER']
    valid=all(r['status']=='SUCCESS' for r in [cold,*jitter]) and cold.get('precision_endpoint_within_registered_tolerance',False)
    hits=sum(r['status']=='SUCCESS' and r['snapshots'][-1]['stable_functional'] for r in jitter)
    h1='PASS' if valid and cold['snapshots'][-1]['stable_functional'] and hits>=6 else ('FAIL' if valid else 'NOT_EVALUABLE')
    summary=dict(study='V204',method='Known LOLA-Ex Eq4.4 with full net individual returns',
        H1=h1,jitter_stable_functional=hits,rows=rows,oracle_not_private_learner=True,
        original_method=False,external_scientific_confirmation=False,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (folder/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V204_DONE',h1,flush=True)


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    main()
