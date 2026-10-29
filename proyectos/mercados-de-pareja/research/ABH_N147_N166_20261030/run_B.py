"""Pre-outcome N151–N154: symmetric dyadic shocks, synthetic equivariance falsifiers."""
import json,time,hashlib
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_equivariant_engine as e
import mini_world as mini
import social_graph_equivariant as canonical
import run_A as a

def audit(kind,slots,policy,seeds=(101,211),reps=3):
    rows=[]
    for seed in seeds:
        p=mini.people(seed)
        def run(x):
            cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':'legacy' if kind=='legacy' else 'pair_max','schedule_slots':slots}
            graph=canonical.build(x,seed,kind) if kind!='legacy' else None
            return e.simulate(seed,'permutation',cfg,people_provider=lambda _:x,compatibility_provider=mini.compatibility,
              population_size=24,steps=4,trace=True,scheduler=canonical.scheduler(graph) if graph else None,shock_policy=policy)
        base=run(p)
        state0,event0=a.normalized(base,np.arange(24))
        for rep in range(reps):
            permutation=np.random.default_rng(seed*1000+rep).permutation(24)
            out=run(a.permuted(p,permutation))
            state1,event1=a.normalized(out,permutation)
            differences=[k for k in state0 if state0[k]!=state1[k]]
            delta=sum((event0-event1).values())+sum((event1-event0).values())
            mismatched_t0=[z for z in (event0-event1)+(event1-event0) if z[0]==0 and z[1]=='formation']
            rows.append(dict(seed=seed,rep=rep,kind=kind,slots=slots,policy=policy,
                  exact=(not differences and delta==0),different_fields=differences,event_difference=delta,
                  first_tick_formation_difference=len(mismatched_t0),baseline_active=state0['active_partnerships_end'],
                  relabel_active=state1['active_partnerships_end']))
    return rows

def check(rows):
    return dict(status='PASS' if all(x['exact'] for x in rows) else 'VALID_NEGATIVE_DIAGNOSTIC',
                exact=sum(x['exact'] for x in rows),checked=len(rows),rows=rows)

def N151():
    r=audit('ring',2,'symmetric_hazard',seeds=(101,),reps=2)
    return dict(**check(r),note='Only hazard symmetric; matching shocks historical; no automatic guarantee whole-path')

def N152():
    r=audit('legacy',1,'symmetric_pair',seeds=(101,),reps=2)
    return dict(**check(r),first_tick_matches_equal=sum(z['first_tick_formation_difference']==0 for z in r))

def N153():
    return check(audit('ring',1,'symmetric_pair')+audit('ring',2,'symmetric_pair'))

def N154():
    return check(audit('rewired',1,'symmetric_pair')+audit('rewired',2,'symmetric_pair')+audit('legacy',1,'symmetric_pair',reps=2))

def main():
    rs=[]
    for fn in (N151,N152,N153,N154):
        st=time.perf_counter()
        try:z=fn()
        except Exception as exc:z=dict(status='INVALID',error=repr(exc))
        rs.append(dict(id=fn.__name__,elapsed_seconds=round(time.perf_counter()-st,3),**z))
        print(fn.__name__,z['status'],z.get('exact'),z.get('checked'),flush=True)
        if z['status']=='INVALID':break
    Path('RESULTS_B.json').write_text(json.dumps(dict(schema='ABH_N151_N154',code_sha256=hashlib.sha256(Path(e.__file__).read_bytes()).hexdigest(),cycles=rs),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
