"""Frozen N160–N163: floating-order repair, complete feedback equivariance, fresh seeds."""
import json,time,hashlib,collections
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_equivariant_engine as old
import esbm_equivariant_engine_v2 as stable
import mini_world as mini
import social_graph_equivariant as graph
import run_A as common

def single(engine,seed,p,kind,slots,private=False,public=False,norm_mode='pair_max'):
    cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':norm_mode,'schedule_slots':slots,'private':private,'public':public}
    g=graph.build(p,seed,kind)
    return engine.simulate(seed,'analysis',cfg,people_provider=lambda _:p,compatibility_provider=mini.compatibility,
      population_size=24,steps=4,trace=True,scheduler=graph.scheduler(g,norm_mode),shock_policy='symmetric_pair')

def N160():
    rows=[]
    for private,public,key in [(True,False,'final_private_aspiration_bias_mean'),(False,True,'final_public_reputation_penalty_mean')]:
        p=mini.people(211)
        for kind in ('ring','rewired'):
            b=single(old,211,p,kind,2,private,public)
            events0=common.normalized(b,np.arange(24))[1]
            for rep in range(3):
                perm=np.random.default_rng(211*1000+rep).permutation(24)
                q=single(old,211,common.permuted(p,perm),kind,2,private,public)
                events1=common.normalized(q,perm)[1]
                err=abs(b[key]-q[key])
                assert err<=1e-12 and events0==events1
                rows.append(dict(kind=kind,rep=rep,mechanism=key,abs_error=err,identical_events=True))
    assert len(rows)==12
    return dict(status='PASS',cases=12,strict_float_mismatches=sum(r['abs_error']!=0 for r in rows),max_abs_error=max(r['abs_error'] for r in rows),rows=rows)

def check_mode(private=False,public=False,seeds=(101,211),norm_mode='pair_max'):
    rows=[]
    for seed in seeds:
        p=mini.people(seed)
        for kind in ('ring','rewired'):
            for slots in (1,2):
                a=single(stable,seed,p,kind,slots,private,public,norm_mode)
                x,y=common.normalized(a,np.arange(24))
                for rep in range(3):
                    perm=np.random.default_rng(seed*1000+rep).permutation(24)
                    b=single(stable,seed,common.permuted(p,perm),kind,slots,private,public,norm_mode)
                    xx,yy=common.normalized(b,perm)
                    dif=[k for k in x if x[k]!=xx[k]]
                    ev=sum((y-yy).values())+sum((yy-y).values())
                    rows.append(dict(seed=seed,kind=kind,slots=slots,rep=rep,exact=not dif and ev==0,fields=dif,events_diff=ev))
    return rows

def N161():
    rows=check_mode(private=True)+check_mode(public=True)
    n=sum(r['exact'] for r in rows)
    old_legacy=0
    for seed in original.SEEDS:
        for label,cfg in original.SCENARIOS.items():
            assert original.simulate(seed,label,cfg)==stable.simulate(seed,label,cfg)
            old_legacy+=1
    return dict(status='PASS' if n==len(rows) else 'VALID_NEGATIVE_DIAGNOSTIC',exact=n,checks=len(rows),legacy_exact=old_legacy,rows=rows)

def N162():
    rows=check_mode(private=True,public=True,seeds=(311,509),norm_mode='pair_norm_same')
    n=sum(r['exact'] for r in rows)
    return dict(status='PASS' if n==24 else 'VALID_NEGATIVE_DIAGNOSTIC',exact=n,checks=24,rows=rows)

def N163():
    rows=[]
    for seed in range(6100,6130):
        p=mini.people(seed)
        for kind in ('ring','rewired'):
            r=single(stable,seed,p,kind,2)
            assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
            rows.append(dict(seed=seed,kind=kind,formed=r['total_relationships_formed'],active=r['active_partnerships_end'],
                             impressions=r['total_impressions'],right_censored=r['right_censored_count']))
    pairs=[]
    for seed in range(6100,6130):
        a=next(x for x in rows if x['seed']==seed and x['kind']=='ring')
        b=next(x for x in rows if x['seed']==seed and x['kind']=='rewired')
        pairs.append(dict(seed=seed,delta_active=a['active']-b['active'],delta_impressions=a['impressions']-b['impressions']))
    d=[x['delta_active'] for x in pairs]
    return dict(status='PASS',runs=len(rows),mean_delta_active=sum(d)/len(d),positive=sum(x>0 for x in d),negative=sum(x<0 for x in d),ties=sum(x==0 for x in d),rows=rows,pairs=pairs)

def main():
    cycles=[]
    for fn in (N160,N161,N162,N163):
        st=time.perf_counter()
        try:out=fn()
        except Exception as err:out=dict(status='INVALID',error=repr(err))
        cycles.append(dict(id=fn.__name__,elapsed_seconds=round(time.perf_counter()-st,3),**out))
        print(fn.__name__,out['status'],out.get('exact'),out.get('checks'),flush=True)
        if out['status']=='INVALID':break
    Path('RESULTS_D.json').write_text(json.dumps(dict(schema='ABH_N160_N163_D',code_sha256=hashlib.sha256(Path(stable.__file__).read_bytes()).hexdigest(),cycles=cycles),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
