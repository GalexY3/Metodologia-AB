"""Test Argon's self-perturbation identification under controlled interference.

We do NOT assume a one-person perturbation is isolated. Simulated unrelated
arrivals/departures are exogenous Poisson events; at lambda=0 the intervention
is controlled and branch is identifiable. At lambda>0, a single own-reward
change can be noisy, so claims of mathematical certainty do not extend.
"""
from pathlib import Path
import json,itertools,numpy as np
HERE=Path(__file__).resolve().parent
rng=np.random.default_rng(20261111)
qcases=(2,4,10,30)
noise_levels=(0,0.1,0.5,1,2,4,8,16)
N=120
rows=[]
for q,lamb in itertools.product(qcases,noise_levels):
 small=q//2;large=q*2
 k=N//q
 for truebranch,n0 in (('under',small),('over',large)):
  S=100_000
  shock=rng.poisson(lamb,S)-rng.poisson(lamb,S)
  # Before r(n0)=0.5 exactly. A single known entrant changes n by+1.
  n1=np.clip(n0+1+shock,1,N)
  r0=min(n0/q,q/n0)
  r1=np.minimum(n1/q,q/n1)
  predicted=np.where(r1>r0,'under',np.where(r1<r0,'over','abstain'))
  correct=float(np.mean(predicted==truebranch))
  cover=float(np.mean(predicted!='abstain'))
  precision=correct/cover if cover else 0
  rows.append(dict(q=q,k=k,initial_n=n0,branch=truebranch,
    independent_noise_rate=lamb,nominal_entrant=1,samples=S,
    unconditional_accuracy=correct,coverage=cover,
    conditional_accuracy=precision))
 for b in ('under','over'):
  z=next(x for x in rows if x['q']==q and x['independent_noise_rate']==lamb and x['branch']==b)
  print('PROBE q',q,'lambda',lamb,'branch',b,
   'unconditional',round(z['unconditional_accuracy'],4),
   'coverage',round(z['coverage'],4),flush=True)
out=HERE/'results'
out.mkdir(parents=True,exist_ok=True)
(out/'active_probe_interference.json').write_text(json.dumps(
 dict(test='single known entrant, unknown independent arrivals/leavers',
      models='one-step reward sign only; no global counts exposed to predictor',
      rows=rows),indent=2),encoding='utf8')
print('PROBE_COMPLETE',len(rows),'conditions',sum(r['samples'] for r in rows),'trials',flush=True)
