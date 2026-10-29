"""AB-H prereg N155–N159, historical parity and social-feedback identity checks."""
import json, time, hashlib
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_equivariant_engine as engine
import mini_world as mini
import social_graph_equivariant as social
import run_A as common

def N155():
    rows=[]
    for seed in original.SEEDS:
        for scenario,c in original.SCENARIOS.items():
            a=original.simulate(seed,scenario,c)
            b=engine.simulate(seed,scenario,c)
            assert a==b,(seed,scenario)
            rows.append(dict(seed=seed,scenario=scenario,formed=a['total_relationships_formed']))
    assert len(rows)==60
    return dict(status='PASS',exact=60,rows=rows)

def compare_learning(private=False,public=False,policy='pair_max',networks=('ring','rewired'),slots_range=(1,2)):
    rows=[]
    for seed in (101,211):
        p=mini.people(seed)
        for kind in networks:
            for slots in slots_range:
                def simulate(x):
                    c={**original.SCENARIOS['mixed_random'],'schedule_mode':policy,'schedule_slots':slots,'private':private,'public':public}
                    g=social.build(x,seed,kind)
                    return engine.simulate(seed,'full',c,shock_policy='symmetric_pair',people_provider=lambda _:x,
                        compatibility_provider=mini.compatibility,population_size=24,steps=4,trace=True,scheduler=social.scheduler(g,policy))
                base=simulate(p)
                stat0,e0=common.normalized(base,np.arange(24))
                for rep in range(3):
                    perm=np.random.default_rng(seed*1000+rep).permutation(24)
                    changed=simulate(common.permuted(p,perm))
                    stat,e=common.normalized(changed,perm)
                    issues=[k for k in stat0 if stat0[k]!=stat[k]]
                    diff=sum((e-e0).values())+sum((e0-e).values())
                    rows.append(dict(seed=seed,network=kind,slots=slots,rep=rep,exact=not issues and diff==0,
                        changed_keys=issues,event_symmetric_difference=diff,base_active=stat0['active_partnerships_end'],relabel_active=stat['active_partnerships_end']))
    return rows

def summarise(rows):
    exact=sum(x['exact'] for x in rows)
    return dict(status='PASS' if exact==len(rows) else 'VALID_NEGATIVE_DIAGNOSTIC',exact=exact,checks=len(rows),rows=rows)

def N156():return summarise(compare_learning(private=True))
def N157():return summarise(compare_learning(public=True))
def N158():
    rows=compare_learning(policy='pair_norm_same',networks=('ring',))+compare_learning(policy='pair_norm_cross',networks=('ring',))
    return summarise(rows)

def N159():
    rng=np.random.default_rng(20261030)
    u=rng.random(100000);v=rng.random(100000);w=np.mod(u+v,1.0)
    m=float(w.mean());cor=float(np.corrcoef(u,w)[0,1])
    assert .497<=m<=.503,(m,'mean')
    assert abs(cor)<.012,(cor,'u-w dependence sample')
    return dict(status='PASS',n=len(w),mean=m,correlation_to_first_shock=cor,predeclared_mean_band=[.497,.503],correlation_abs_cap=.012)

def main():
    cycles=[]
    for fn in (N155,N156,N157,N158,N159):
        st=time.perf_counter()
        try:z=fn()
        except Exception as exc:z=dict(status='INVALID',error=repr(exc))
        cycles.append(dict(id=fn.__name__,seconds=round(time.perf_counter()-st,3),**z))
        print(fn.__name__,z['status'],z.get('exact'),z.get('checks'),flush=True)
        if z['status']=='INVALID':break
    result=dict(schema='ABH_N155_N159_C',code_sha256=hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest(),cycles=cycles)
    Path('RESULTS_C.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
