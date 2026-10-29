"""AB-H N147-N150: prereg A-J at GitHub, actor identity full-trajectory test.
Synthetic only; failures are preserved as negative diagnostic, not silently dropped.
"""
import json, time, collections, hashlib
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_event_engine as engine
import mini_world as mini
import social_graph_equivariant as canonical

SEEDS=(101,211)
PERMS=3

def permuted(p,perm):
    return {k:(v[:,perm,:][:,:,perm].copy() if isinstance(v,np.ndarray) and v.ndim==3
             else v[perm].copy() if isinstance(v,np.ndarray) and v.ndim==1 else v)
            for k,v in p.items()}

def run_state(seed,p,kind,slots,mode='pair_max'):
    graph=canonical.build(p,seed,kind) if kind!='legacy' else None
    cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':'legacy' if kind=='legacy' else mode,'schedule_slots':slots}
    out=engine.simulate(seed,'permutation',cfg,people_provider=lambda _:p,compatibility_provider=mini.compatibility,
         population_size=24,steps=4,trace=True,scheduler=canonical.scheduler(graph) if graph is not None else None)
    return out

def normalized(r,actor_map):
    rest={k:v for k,v in r.items() if k!='events'}
    events=[]
    for e in r['events']:
        a,b=int(actor_map[e['i']]),int(actor_map[e['j']])
        if e['stage'] in ('formation','dissolution'): a,b=sorted((a,b))
        events.append((e['t'],e['stage'],a,b))
    return rest,collections.Counter(events)

def audit(kind,slots,seeds=SEEDS,perms=PERMS):
    rows=[]
    for seed in seeds:
        original_p=mini.people(seed)
        initial=run_state(seed,original_p,kind,slots)
        base_state,base_events=normalized(initial,np.arange(24))
        for rep in range(perms):
            perm=np.random.default_rng(seed*1000+rep).permutation(24)
            p2=permuted(original_p,perm)
            challenger=run_state(seed,p2,kind,slots)
            state,events=normalized(challenger,perm)
            mismatched_keys=[k for k in base_state if base_state[k]!=state[k]]
            event_delta=sum((base_events-events).values())+sum((events-base_events).values())
            rows.append(dict(seed=seed,rep=rep,mode=kind,slots=slots,
                aggregates_equal=not mismatched_keys,events_equal=event_delta==0,
                mismatched_keys=mismatched_keys,event_symmetric_difference=event_delta,
                original_formed=base_state['total_relationships_formed'],permuted_formed=state['total_relationships_formed'],
                original_active=base_state['active_partnerships_end'],permuted_active=state['active_partnerships_end']))
    return rows

def N147():
    rows=audit('ring',1)+audit('ring',2)
    assert len(rows)==12
    passed=sum(z['aggregates_equal'] and z['events_equal'] for z in rows)
    return dict(status='PASS' if passed==12 else 'VALID_NEGATIVE_DIAGNOSTIC',checks=12,exact=passed,rows=rows)

def N148():
    rows=audit('rewired',1)+audit('rewired',2)
    assert len(rows)==12
    passed=sum(z['aggregates_equal'] and z['events_equal'] for z in rows)
    return dict(status='PASS' if passed==12 else 'VALID_NEGATIVE_DIAGNOSTIC',checks=12,exact=passed,rows=rows)

def N149(r147,r148):
    failures=[z for z in r147['rows']+r148['rows'] if not z['aggregates_equal'] or not z['events_equal']]
    if not failures:
        return dict(status='PASS',diagnostic='All 24 preselected full trajectories match',failures=[])
    first=failures[0]
    return dict(status='VALID_NEGATIVE_DIAGNOSTIC',counterexamples=len(failures),first=first,
                suspect='actor ID dependent evaluation order or u_match upper-triangle shock; inspect before repair',
                all_failing_cases=failures)

def N150():
    rows=audit('legacy',1,seeds=(101,211),perms=2)
    assert len(rows)==4
    passed=sum(z['aggregates_equal'] and z['events_equal'] for z in rows)
    return dict(status='PASS' if passed==4 else 'VALID_NEGATIVE_DIAGNOSTIC',checks=4,exact=passed,rows=rows)

def main():
    results=[]
    for f in (N147,N148):
        started=time.perf_counter()
        try:r=f()
        except Exception as exc:r=dict(status='INVALID',error=repr(exc))
        results.append(dict(id=f.__name__,elapsed_seconds=round(time.perf_counter()-started,3),**r))
        print(f.__name__,r['status'],flush=True)
        if r['status']=='INVALID':break
    if len(results)==2:
        for f,args in [(N149,(results[0],results[1])),(N150,())]:
            started=time.perf_counter()
            try:r=f(*args)
            except Exception as exc:r=dict(status='INVALID',error=repr(exc))
            results.append(dict(id=f.__name__,elapsed_seconds=round(time.perf_counter()-started,3),**r))
            print(f.__name__,r['status'],flush=True)
            if r['status']=='INVALID':break
    receipt=dict(schema='ABH_N147_N150_A',source_sha256=hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest(),cycles=results)
    Path('RESULTS_A.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
