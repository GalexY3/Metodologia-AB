"""Private-fitness evolution with explicit competent affine rivals."""
import os
os.environ.setdefault('NUMBA_NUM_THREADS','3')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import time
from numba import njit,prange
import numpy as np
from research_resource_limits import apply_limits

ROOT=Path(__file__).resolve().parent
MODES={'FULL':0,'ORIGINAL_PRIVATE':1,'AFFINE_PRIVATE':2,'AFFINE_FULL':3,'PRIVATE_THRESHOLD':4}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2),encoding='utf8');tmp.replace(path)


@njit(cache=True,parallel=True,fastmath=False)
def generation(theta,y0,mode,steps=1000,trace=False):
    n,m,_=theta.shape;fit=np.zeros((n,m));rates=np.zeros((n,m));stock=np.zeros(n)
    acts=np.zeros((steps,n,m),np.int8) if trace else np.zeros((1,1,1),np.int8)
    xs=np.zeros((steps,n)) if trace else np.zeros((1,1))
    for group in prange(n):
        y=y0[group].copy();h=np.zeros(m,np.int8);x=.1
        for t in range(steps):
            total=0.
            for i in range(m):total+=y[i]
            for i in range(m):
                g=theta[group,i]
                if mode==0:score=x+(g[0]*m)*y[i]+g[1]*(m*total/m)
                elif mode==1:score=x+(g[0]*m)*y[i]
                elif mode==2:score=x+(g[0]*m)*y[i]+g[1]
                elif mode==3:score=x+(g[0]*m)*y[i]+g[1]*(m*total/m)+g[2]
                else:score=g[0]-m*y[i]
                h[i]=int(score>0.)
                if trace:acts[t,group,i]=h[i]
                if t>=int(round(.1*steps)):fit[group,i]+=y[i]
                rates[group,i]+=h[i]
            if trace:xs[t,group]=x
            H=0
            for i in range(m):H+=h[i]
            grown=x+(x-x*x);harvested=min((.9/m)*H,1.)*grown
            x=grown-harvested;unit=harvested/H if H>0 else 0.
            for i in range(m):y[i]=.75*y[i]+unit*h[i]
            stock[group]+=x
        stock[group]/=steps
        for i in range(m):
            fit[group,i]/=steps-int(round(.1*steps));rates[group,i]/=steps
    return fit,rates,stock,acts,xs


def reference(theta,y0,mode,steps):
    n,m,_=theta.shape;y=y0.copy();x=np.full(n,.1);fit=np.zeros_like(y);aa=[];xx=[]
    for t in range(steps):
        own=(theta[:,:,0]*m)*y
        if mode==0:z=x[:,None]+own+theta[:,:,1]*(m*y.sum(1,keepdims=True)/m)
        elif mode==1:z=x[:,None]+own
        elif mode==2:z=x[:,None]+own+theta[:,:,1]
        elif mode==3:z=x[:,None]+own+theta[:,:,1]*(m*y.sum(1,keepdims=True)/m)+theta[:,:,2]
        else:z=theta[:,:,0]-m*y
        h=(z>0).astype(np.int8);aa.append(h);xx.append(x.copy())
        if t>=int(round(.1*steps)):fit+=y
        H=h.sum(1);grown=x+(x-x*x);harvested=np.minimum((.9/m)*H,1)*grown
        unit=np.divide(harvested,H,out=np.zeros(n),where=H>0)
        x=grown-harvested;y=.75*y+unit[:,None]*h
    return fit/(steps-int(round(.1*steps))),np.array(aa),np.array(xx)


def audit():
    limits=apply_limits(3);rng=np.random.default_rng(178900);rows=[]
    for m in (3,5,16):
        for name,mode in MODES.items():
            th=rng.normal(0,.4,(24,m,3));y0=(1+rng.normal(0,.1,(24,m)))/m
            got=generation(th,y0,mode,120,True);ref=reference(th,y0,mode,120)
            err=max(float(np.max(abs(got[0]-ref[0]))),float(np.max(abs(got[4]-ref[2]))))
            mismatch=int(np.sum(got[3]!=ref[1]));assert err<1e-12 and mismatch==0,(m,name,err,mismatch)
            if name in ('ORIGINAL_PRIVATE','AFFINE_PRIVATE','PRIVATE_THRESHOLD'):
                other=y0.copy();other[:,1:]*=10
                before=generation(th,y0,mode,1,True)[3][:,:,0]
                after=generation(th,other,mode,1,True)[3][:,:,0]
                assert np.array_equal(before,after)
            rows.append(dict(m=m,mode=name,max_error=err,action_mismatches=mismatch))
    p=ROOT/'literatura/original_code/Itao_ds_game_multi_player.py'
    spec=importlib.util.spec_from_file_location('v178_original_audit',p);src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
    th=rng.normal(0,.5,(200,5,3));th[:,:,0]=-rng.uniform(1,6,(200,5));th[:,:,1]=-th[:,:,0]/1.2
    y0=(1+rng.normal(0,.1,(200,5)))/5
    ref=src.play_generation(th[:,:,0],th[:,:,1],rng,num_steps=500,y0=y0,record_groups=200,record_steps=500)
    got=generation(th,y0,0,500,True)
    err=float(np.max(abs(got[0]-ref['fit'])));mismatch=int(np.sum(got[3]!=ref['trace']['h']))
    assert err<1e-12 and mismatch==0
    return dict(limits=limits,source_sha256=sha(__file__),reference=rows,
                original_parity=dict(sha256=sha(p),groups=200,steps=500,fitness_error=err,action_mismatches=mismatch))


def worker(seed,name,m,outdir):
    limits=apply_limits(3);out=Path(outdir)/f'{name}_{seed}';out.mkdir(exist_ok=False)
    rng=np.random.default_rng([seed,100,m]);theta=rng.normal(0,.1,(100*m,3));curve=[];start=time.perf_counter()
    init=hashlib.sha256(theta.tobytes()).hexdigest();save(out/'RESOURCE_STATE.json',limits)
    for g in range(3000):
        theta=theta[rng.permutation(100*m)];y0=(1+rng.normal(0,.1,(100,m)))/m
        fit,rates,resource,_,_=generation(theta.reshape(100,m,3),y0,MODES[name])
        individual=fit.reshape(-1);total=individual.sum();assert np.isfinite(total) and total>=0
        curve.append(dict(generation=g+1,Q=float(fit.sum(1).mean()),harvest=float(rates.mean()),resource=float(resource.mean())))
        if g==2999:np.savez_compressed(out/'FINAL_POPULATION.npz',theta=theta,y0=y0,fit=fit)
        parents=rng.choice(100*m,size=100*m,p=individual/total) if total>0 else rng.integers(0,100*m,size=100*m)
        theta=theta[parents]+rng.normal(0,.1,(100*m,3))
        if (g+1)%500==0:
            np.savez_compressed(out/f'CHECKPOINT_{g+1:04}.npz',theta_next=theta,curve_Q=np.array([r['Q'] for r in curve]))
            save(out/f'RNG_{g+1:04}.json',rng.bit_generator.state)
            with (out/'PROGRESS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(**curve[-1],elapsed=time.perf_counter()-start))+'\n')
    result=dict(seed=seed,mode=name,m=m,Q_tail=float(np.mean([r['Q'] for r in curve[-500:]])),
                initial_genotype_sha256=init,resource_limits=limits,elapsed=time.perf_counter()-start,all_generations=3000)
    save(out/'CURVE.json',curve);save(out/'RESULT.json',result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit-only',action='store_true');p.add_argument('--prereg-commit');p.add_argument('--m',type=int,default=5,choices=(5,16));args=p.parse_args()
    if args.audit_only:
        out=ROOT/'results/V178_PRE_RUN_AUDIT.json';assert not out.exists();result=audit();save(out,result);print('V178_AUDIT',json.dumps(result),flush=True);return
    assert args.prereg_commit and len(args.prereg_commit)==40
    pre=json.loads((ROOT/'results/V178_PRE_RUN_AUDIT.json').read_text());assert pre['source_sha256']==sha(__file__)
    if args.m==16:
        parent=json.loads((ROOT/'results/v178_private_affine_M5/SUMMARY.json').read_text())
        assert parent['primary_gate'] and parent['full_control_gate'],'M16 not authorized by the preregistered M5 gates'
    seeds=tuple(range(178115,178123)) if args.m==5 else tuple(range(178215,178223))
    out=ROOT/f'results/v178_private_affine_M{args.m}';out.mkdir(exist_ok=False)
    freeze=dict(prereg_commit=args.prereg_commit,source_sha256=sha(__file__),
                protocol_sha256=sha(ROOT/'PREREG_V178_PRIVATE_AFFINE_RIVAL.md'),seeds=seeds,m=args.m,
                modes=MODES,generations=3000,steps=1000,groups=100,genes=3,mutation_sd=.1,
                max_workers=2,threads_per_worker=3,audit_sha256=sha(ROOT/'results/V178_PRE_RUN_AUDIT.json'))
    save(out/'FREEZE.json',freeze);rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(worker,seed,name,args.m,str(out)) for seed in seeds for name in MODES]
        for future in concurrent.futures.as_completed(jobs):
            result=future.result();rows.append(result);print('V178_FINISHED',json.dumps(result),flush=True)
    pair=[]
    for seed in seeds:
        rr=[r for r in rows if r['seed']==seed];assert len({r['initial_genotype_sha256'] for r in rr})==1
        q={r['mode']:r['Q_tail'] for r in rr}
        pair.append(dict(seed=seed,Q=q,affine_private_gain=q['AFFINE_PRIVATE']-q['ORIGINAL_PRIVATE'],
                         affine_private_minus_full=q['AFFINE_PRIVATE']-q['FULL']))
    primary=sum(r['Q']['AFFINE_PRIVATE']>=.7 for r in pair)>=6 and np.median([r['affine_private_gain'] for r in pair])>=.2
    control=sum(r['Q']['FULL']>=.7 for r in pair)>=6
    summary=dict(freeze=freeze,results=rows,paired=pair,primary_gate=bool(primary),full_control_gate=bool(control),
                 training_seed_count=8,external_confirmation=False,CT2=61,N2=0)
    save(out/'SUMMARY.json',summary);print('V178_DONE',json.dumps(pair),'GATES',primary,control,flush=True)


if __name__=='__main__':main()
