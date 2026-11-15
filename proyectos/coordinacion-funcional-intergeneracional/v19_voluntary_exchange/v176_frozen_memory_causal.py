"""Prospective frozen-policy interventions after the completed V175 pilot."""
import os
os.environ.setdefault('NUMBA_NUM_THREADS','3')
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse
import hashlib
import json
import math
from pathlib import Path
import numba
from numba import njit, prange
import numpy as np
from research_resource_limits import apply_limits
from v175_memory_evolution import generation as prior_generation, MODES, save_json

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'results/v175_learned_memory'
SEEDS=(175115,175116)
BATCHES=tuple(range(176115,176123))
NAMES=('RNN_RESOURCE','RNN_FULL','MLP_RESOURCE','LINEAR_FULL')
LESIONS={'INTACT':0,'RESET':1,'RESOURCE_CLAMP':2,'SENSORY_CLAMP':3,
         'CLONAL_GROUPS':4,'ALWAYS_HARVEST_INVADER':5}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@njit(cache=True,parallel=True,fastmath=False)
def evaluate(theta,y0,mode,lesion,steps=1000,trace=False):
    n,m,_=theta.shape
    fit=np.zeros((n,m));rates=np.zeros((n,m));switches=np.zeros((n,m));stock=np.zeros(n)
    actions=np.zeros((steps,n,m),np.int8) if trace else np.zeros((1,1,1),np.int8)
    resources=np.zeros((steps,n)) if trace else np.zeros((1,1))
    for group in prange(n):
        y=y0[group].copy();hidden=np.zeros((m,4));next_hidden=np.zeros((m,4))
        act=np.zeros(m,np.int8);old_act=np.zeros(m,np.int8);x=.1
        for t in range(steps):
            total=0.
            for i in range(m):total+=y[i]
            obsx=.1 if lesion==2 or lesion==3 else x
            for i in range(m):
                g=theta[group,i]
                obsy=1. if lesion==3 else m*y[i]
                obstotal=1. if lesion==3 else total
                if mode==3:
                    # Maintain the original multiplication order for parity.
                    own=(g[0]*m)*(1./m if lesion==3 else y[i])
                    peer=m*obstotal/m
                    score=obsx+own+g[1]*peer
                else:
                    for h in range(4):
                        peer=obstotal if mode==1 else 0.
                        z=g[3*h]*obsx+g[3*h+1]*obsy+g[3*h+2]*peer+g[28+h]
                        if mode!=2 and lesion!=1:
                            for j in range(4):z+=g[12+4*h+j]*hidden[i,j]
                        next_hidden[i,h]=math.tanh(z)
                    score=g[36]
                    for h in range(4):score+=g[32+h]*next_hidden[i,h]
                act[i]=1 if lesion==5 and i==0 else int(score>0.)
                if trace:actions[t,group,i]=act[i]
                if t>=int(round(.1*steps)):fit[group,i]+=y[i]
                rates[group,i]+=act[i]
                if t>0:switches[group,i]+=abs(int(act[i])-int(old_act[i]))
                old_act[i]=act[i]
            if trace:resources[t,group]=x
            H=0
            for i in range(m):H+=act[i]
            grown=x+(x-x*x);harvested=min((.9/m)*H,1.)*grown
            unit=harvested/H if H>0 else 0.
            x=grown-harvested
            for i in range(m):
                y[i]=.75*y[i]+unit*act[i]
                if mode<3:
                    for h in range(4):hidden[i,h]=next_hidden[i,h]
            stock[group]+=x
        stock[group]/=steps
        for i in range(m):
            fit[group,i]/=steps-int(round(.1*steps))
            rates[group,i]/=steps;switches[group,i]/=max(1,steps-1)
    return fit,rates,switches,stock,actions,resources


def audit():
    limits=apply_limits(3);rng=np.random.default_rng(176900);rows=[]
    for m in (3,5,8,16):
        for name in NAMES:
            theta=rng.normal(0,.4,(12,m,37));y0=(1+rng.normal(0,.1,(12,m)))/m
            a=prior_generation(theta,y0,MODES[name],120,True)
            b=evaluate(theta,y0,MODES[name],0,120,True)
            err=max(float(np.max(abs(a[0]-b[0]))),float(np.max(abs(a[4]-b[5]))))
            mismatch=int(np.sum(a[3]!=b[4]));assert err<1e-12 and mismatch==0,(m,name,err,mismatch)
            if name in ('MLP_RESOURCE','LINEAR_FULL'):
                reset=evaluate(theta,y0,MODES[name],1,120,True)
                assert np.array_equal(b[4],reset[4]) and np.array_equal(b[0],reset[0])
            rows.append(dict(m=m,mode=name,max_error=err,action_mismatches=mismatch))
    frozen=[]
    # All ten stored V175 endpoints, including the structured filter.
    for path in sorted(SOURCE.glob('*/FINAL_POPULATION.npz')):
        name=path.parent.name.rsplit('_',1)[0];a=np.load(path)
        fit=prior_generation(a['theta'].reshape(100,5,37),a['y0'],MODES[name])[0]
        error=float(np.max(abs(fit-a['fit'])));assert error==0.,(str(path),error)
        frozen.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),max_error=error))
    assert len(frozen)==10
    return dict(limits=limits,kernel_parity=rows,V175_endpoints=frozen,
                source_sha256=sha(__file__),V175_source_sha256=sha(ROOT/'v175_memory_evolution.py'),
                resource_limits_sha256=sha(ROOT/'research_resource_limits.py'))


def run(commit):
    limits=apply_limits(3);pre=json.loads((ROOT/'results/V176_PRE_RUN_AUDIT.json').read_text())
    assert sha(__file__)==pre['source_sha256']
    out=ROOT/'results/v176_frozen_memory';out.mkdir(exist_ok=False)
    save_json(out/'FREEZE.json',dict(prereg_commit=commit,source_sha256=sha(__file__),
                protocol_sha256=sha(ROOT/'PREREG_V176_FROZEN_MEMORY_CAUSAL.md'),audit=pre,limits=limits))
    summaries=[]
    for seed in SEEDS:
        for name in NAMES:
            population=np.load(SOURCE/f'{name}_{seed}/FINAL_POPULATION.npz')['theta']
            for m in (5,3,8,16):
                if m!=5 and name not in ('RNN_RESOURCE','LINEAR_FULL'):continue
                conditions=LESIONS if m==5 else {'INTACT':0,'RESET':1}
                values={label:[] for label in conditions}
                raw={label:[] for label in conditions}
                for batch in BATCHES:
                    rng=np.random.default_rng([batch,seed,m]);idx=rng.integers(0,500,(128,m))
                    theta=population[idx];y0=(1+rng.normal(0,.1,(128,m)))/m
                    for label,lesion in conditions.items():
                        tt=np.repeat(theta[:,0:1,:],m,axis=1) if lesion==4 else theta
                        fit,rate,sw,stock,_,_=evaluate(tt,y0,MODES[name],lesion)
                        q=fit.sum(1)
                        row=dict(batch=batch,Q=float(q.mean()),focal_fitness=float(fit[:,0].mean()),
                                 others_fitness=float(fit[:,1:].sum(1).mean()),harvest=float(rate.mean()),
                                 switches=float(sw.mean()),resource=float(stock.mean()),
                                 group_Q_quantiles=np.quantile(q,[0,.25,.5,.75,1]).tolist())
                        values[label].append(row)
                        raw[label].append(dict(batch=batch,Q=q.tolist(),fit=fit.tolist(),
                                              rates=rate.tolist(),switches=sw.tolist(),resource=stock.tolist()))
                mean={label:{k:float(np.mean([r[k] for r in rr])) for k in
                    ('Q','focal_fitness','others_fitness','harvest','switches','resource')}
                    for label,rr in values.items()}
                causal=dict(recurrence_gain=mean['INTACT']['Q']-mean['RESET']['Q'])
                if m==5:
                    causal.update(resource_feedback_gain=mean['INTACT']['Q']-mean['RESOURCE_CLAMP']['Q'],
                        sensory_feedback_gain=mean['INTACT']['Q']-mean['SENSORY_CLAMP']['Q'],
                        diversity_gain=mean['INTACT']['Q']-mean['CLONAL_GROUPS']['Q'],
                        invader_private_gain=mean['ALWAYS_HARVEST_INVADER']['focal_fitness']-mean['INTACT']['focal_fitness'],
                        invader_group_gain=mean['ALWAYS_HARVEST_INVADER']['Q']-mean['INTACT']['Q'])
                summary=dict(seed=seed,mode=name,m=m,means=mean,contrasts=causal,batches=values)
                summaries.append(summary)
                save_json(out/f'{name}_{seed}_M{m}.json',dict(summary=summary,groups=raw))
                print('V176',seed,name,m,json.dumps(dict(means=mean,contrasts=causal)),flush=True)
    rr=[r for r in summaries if r['mode']=='RNN_RESOURCE' and r['m']==5]
    tests=dict(recurrence_necessary_in_both=all(r['contrasts']['recurrence_gain']>=.15 for r in rr),
               no_variable_sensory_capacity_in_both=all(r['means']['SENSORY_CLAMP']['Q']>=.3 and
                   abs(r['contrasts']['sensory_feedback_gain'])<=.05 for r in rr),
               exploitable_by_always_harvest_in_both=all(r['contrasts']['invader_private_gain']>=.02 for r in rr))
    save_json(out/'SUMMARY.json',dict(results=summaries,tests=tests,training_seeds=2,
             independent_evolution_replication=False,independent_external_confirmation=False,CT2=61,N2=0))
    print('V176_DONE',tests,flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit-only',action='store_true');p.add_argument('--prereg-commit')
    args=p.parse_args()
    if args.audit_only:
        target=ROOT/'results/V176_PRE_RUN_AUDIT.json';assert not target.exists()
        result=audit();save_json(target,result);print('V176_AUDIT',json.dumps(result),flush=True)
    else:
        assert args.prereg_commit and len(args.prereg_commit)==40
        run(args.prereg_commit)


if __name__=='__main__':main()
