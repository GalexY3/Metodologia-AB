"""Private-fitness evolution with generic or structured resource memory.

Environment after Itao & Kaneko, arXiv:2507.22555v2. Independently implemented
float64 dynamics. No prescribed observer coefficients in learned-memory arms.
"""
import os
os.environ.setdefault('NUMBA_NUM_THREADS','3')
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import time
import numba
from numba import njit,prange
import numpy as np
from research_resource_limits import apply_limits

ROOT=Path(__file__).resolve().parent
MODES={'RNN_RESOURCE':0,'RNN_FULL':1,'MLP_RESOURCE':2,'LINEAR_FULL':3,'FILTER_RESOURCE':4}
SEEDS=(175115,175116)
GENES=37


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@njit(cache=True,parallel=True,fastmath=False)
def generation(theta,y0,mode,steps=1000,trace=False):
    n,m,_=theta.shape
    fit=np.zeros((n,m));rates=np.zeros((n,m));stock=np.zeros(n)
    actions=np.zeros((steps,n,m),np.int8) if trace else np.zeros((1,1,1),np.int8)
    resources=np.zeros((steps,n)) if trace else np.zeros((1,1))
    for group in prange(n):
        y=y0[group].copy();hidden=np.zeros((m,4));next_hidden=np.zeros((m,4))
        memory=np.zeros(m);act=np.zeros(m,np.int8);x=.1
        for t in range(steps):
            total=0.
            for i in range(m):total+=y[i]
            for i in range(m):
                g=theta[group,i]
                if mode==3:
                    # Same operation order as the original NumPy perceptron.
                    peer=m*total/m
                    score=x+(g[0]*m)*y[i]+g[1]*peer
                elif mode==4:
                    score=x+(g[0]*m)*y[i]+g[1]*memory[i]
                else:
                    for h in range(4):
                        peer=total if mode==1 else 0.
                        z=g[3*h]*x+g[3*h+1]*(m*y[i])+g[3*h+2]*peer+g[28+h]
                        if mode!=2:
                            for j in range(4):z+=g[12+4*h+j]*hidden[i,j]
                        next_hidden[i,h]=math.tanh(z)
                    score=g[36]
                    for h in range(4):score+=g[32+h]*next_hidden[i,h]
                act[i]=int(score>0.)
                if trace:actions[t,group,i]=act[i]
                if t>=int(round(.1*steps)):fit[group,i]+=y[i]
                rates[group,i]+=act[i]
            if trace:resources[t,group]=x
            H=0
            for i in range(m):H+=act[i]
            grown=x+(x-x*x)
            harvested=min((.9/m)*H,1.)*grown
            unit=harvested/H if H>0 else 0.
            xx=grown-harvested
            for i in range(m):
                y[i]=.75*y[i]+unit*act[i]
                if mode==4:
                    g=theta[group,i]
                    lag=1./(1.+math.exp(-min(60.,max(-60.,g[2]))))
                    # Only the consecutive resource observations enter memory.
                    memory[i]=lag*memory[i]+g[3]*x+g[4]*x*x+g[5]*xx
                if mode<3:
                    for h in range(4):hidden[i,h]=next_hidden[i,h]
            x=xx;stock[group]+=x
        for i in range(m):
            fit[group,i]/=steps-int(round(.1*steps))
            if not math.isfinite(fit[group,i]) or fit[group,i]<=0:fit[group,i]=0.
            rates[group,i]/=steps
        stock[group]/=steps
    return fit,rates,stock,actions,resources


def numpy_reference(theta,y0,mode,steps):
    n,m,_=theta.shape;y=y0.copy();x=np.full(n,.1);hidden=np.zeros((n,m,4));memory=np.zeros((n,m))
    fit=np.zeros_like(y);rates=np.zeros_like(y);hs=[];xs=[]
    for t in range(steps):
        total=y.sum(1,keepdims=True)
        if mode==3:score=x[:,None]+(theta[:,:,0]*m)*y+theta[:,:,1]*(m*total/m)
        elif mode==4:score=x[:,None]+(theta[:,:,0]*m)*y+theta[:,:,1]*memory
        else:
            obs=np.stack([np.broadcast_to(x[:,None],(n,m)),m*y,
                          np.broadcast_to(total,(n,m)) if mode==1 else np.zeros_like(y)],axis=-1)
            hh=np.einsum('nmhi,nmi->nmh',theta[:,:,:12].reshape(n,m,4,3),obs)+theta[:,:,28:32]
            if mode!=2:hh+=np.einsum('nmhj,nmj->nmh',theta[:,:,12:28].reshape(n,m,4,4),hidden)
            hidden=np.tanh(hh)
            score=(theta[:,:,32:36]*hidden).sum(-1)+theta[:,:,36]
        h=(score>0).astype(np.int8);hs.append(h.copy());xs.append(x.copy())
        if t>=int(round(.1*steps)):fit+=y
        rates+=h;H=h.sum(1);grown=x+(x-x*x);harvested=np.minimum((.9/m)*H,1.)*grown
        unit=np.divide(harvested,H,out=np.zeros(n),where=H>0)
        xx=grown-harvested
        if mode==4:
            lag=1/(1+np.exp(-np.clip(theta[:,:,2],-60,60)))
            memory=lag*memory+theta[:,:,3]*x[:,None]+theta[:,:,4]*x[:,None]**2+theta[:,:,5]*xx[:,None]
        x=xx;y=.75*y+unit[:,None]*h
    return fit/(steps-int(round(.1*steps))),rates/steps,np.array(hs),np.array(xs)


def audit():
    limits=apply_limits();rng=np.random.default_rng(175900);rows=[]
    for m in (3,5,8):
        for name,mode in MODES.items():
            theta=rng.normal(0,.4,(12,m,37));y0=(1+rng.normal(0,.1,(12,m)))/m
            c=generation(theta,y0,mode,120,True);ref=numpy_reference(theta,y0,mode,120)
            errors=[float(np.max(np.abs(c[0]-ref[0]))),float(np.max(np.abs(c[4]-ref[3])))]
            mismatch=int(np.sum(c[3]!=ref[2]))
            assert max(errors)<1e-12 and mismatch==0,(m,name,errors,mismatch)
            rows.append(dict(m=m,mode=name,fitness_error=errors[0],resource_error=errors[1],action_mismatches=mismatch))
    original=ROOT/'literatura/original_code/Itao_ds_game_multi_player.py'
    assert original.exists(),'Recover the public original for the pre-run physics audit (not needed by the training kernel).'
    spec=importlib.util.spec_from_file_location('v175_original_audit',original)
    src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
    theta=rng.normal(0,.5,(200,5,37));theta[:,:,0]=-rng.uniform(1,6,(200,5));theta[:,:,1]=-theta[:,:,0]/1.2
    y0=(1+rng.normal(0,.1,(200,5)))/5
    ref=src.play_generation(theta[:,:,0],theta[:,:,1],rng,num_steps=500,y0=y0,record_groups=200,record_steps=500)
    got=generation(theta,y0,3,500,True)
    error=float(np.max(np.abs(got[0]-ref['fit'])));mismatch=int(np.sum(got[3]!=ref['trace']['h']))
    assert error<1e-12 and mismatch==0,(error,mismatch)
    # Static input-isolation test: no group state is passed to a resource-only
    # individual's neural score. Changing other wealth leaves its action intact.
    info=[]
    for name,mode in MODES.items():
        ta=rng.normal(0,.4,(2,5,37));yy=np.ones((2,5))*.2;yb=yy.copy();yb[:,1:]*=4
        aa=generation(ta,yy,mode,1,True)[3][:,:,0]
        bb=generation(ta,yb,mode,1,True)[3][:,:,0]
        if name not in ('RNN_FULL','LINEAR_FULL'):assert np.array_equal(aa,bb),name
        info.append(dict(mode=name,resource_only_input_gate=name not in ('RNN_FULL','LINEAR_FULL')))
    return dict(limits=limits,numerical_reference=rows,
                original_parity=dict(groups=200,steps=500,fitness_max_error=error,action_mismatches=mismatch,sha256=sha(original)),
                input_isolation=info,source_sha256=sha(__file__),resource_limits_sha256=sha(ROOT/'research_resource_limits.py'),
                numpy=np.__version__,numba=numba.__version__)


def save_json(path,obj):
    temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_text(json.dumps(obj,indent=2),encoding='utf8');temporary.replace(path)


def worker(seed,name,outdir):
    from numba import set_num_threads
    limits=apply_limits(3);set_num_threads(3)
    out=Path(outdir)/f'{name}_{seed}';out.mkdir(exist_ok=False)
    save_json(out/'RESOURCE_STATE.json',limits)
    rng=np.random.default_rng([seed,100,5]);theta=rng.normal(0,.1,(500,37))
    initial_hash=hashlib.sha256(theta.tobytes()).hexdigest();curve=[];start=time.perf_counter()
    last_theta=last_y0=last_fit=None
    mode=MODES[name]
    for g in range(3000):
        theta=theta[rng.permutation(500)]
        y0=(1+rng.normal(0,.1,(100,5)))/5
        fit,rates,resource,_,_=generation(theta.reshape(100,5,37),y0,mode)
        individual=fit.reshape(-1)
        row=dict(generation=g+1,Q=float(fit.sum(1).mean()),harvest=float(rates.mean()),resource=float(resource.mean()))
        curve.append(row)
        if g==2999:last_theta=theta.copy();last_y0=y0.copy();last_fit=fit.copy()
        total=individual.sum()
        parents=rng.choice(500,size=500,p=individual/total) if total>0 and np.isfinite(total) else rng.integers(0,500,size=500)
        theta=theta[parents]+rng.normal(0,.1,(500,37))
        if (g+1)%250==0:
            with (out/'PROGRESS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(**row,elapsed=time.perf_counter()-start))+'\n')
        if (g+1)%500==0:
            target=out/f'CHECKPOINT_{g+1:04}.npz';tmp=target.with_suffix('.tmp')
            with tmp.open('wb') as f:np.savez_compressed(f,theta_next=theta,curve_Q=np.array([r['Q'] for r in curve]),next_generation=g+1)
            tmp.replace(target);save_json(out/f'RNG_{g+1:04}.json',rng.bit_generator.state)
    np.savez_compressed(out/'FINAL_POPULATION.npz',theta=last_theta,y0=last_y0,fit=last_fit)
    tail=float(np.mean([r['Q'] for r in curve[-500:]]))
    result=dict(seed=seed,mode=name,Q_tail=tail,initial_genotype_sha256=initial_hash,
                elapsed=time.perf_counter()-start,resource_limits=limits,
                all_generations=3000,individual_fitness_selection=True,
                observer_coefficients_supplied=False,policy_parameters_learned_by_evolution=True)
    save_json(out/'CURVE.json',curve);save_json(out/'RESULT.json',result)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit-only',action='store_true');p.add_argument('--prereg-commit')
    args=p.parse_args()
    if args.audit_only:
        out=ROOT/'results/V175_PRE_RUN_AUDIT.json';assert not out.exists()
        info=audit();save_json(out,info);print('V175_AUDIT',json.dumps(info),flush=True);return
    assert args.prereg_commit and len(args.prereg_commit)==40,'Remote prereg commit must be supplied.'
    pre=json.loads((ROOT/'results/V175_PRE_RUN_AUDIT.json').read_text())
    assert pre['source_sha256']==sha(__file__) and pre['resource_limits_sha256']==sha(ROOT/'research_resource_limits.py')
    out=ROOT/'results/v175_learned_memory';out.mkdir(exist_ok=False)
    freeze=dict(study='V175',prereg_commit=args.prereg_commit,source_sha256=sha(__file__),
                protocol_sha256=sha(ROOT/'PREREG_V175_LEARNED_ECOLOGICAL_MEMORY.md'),
                resource_limits_sha256=sha(ROOT/'research_resource_limits.py'),pre_run_audit_sha256=sha(ROOT/'results/V175_PRE_RUN_AUDIT.json'),
                modes=MODES,seeds=SEEDS,groups=100,group_size=5,steps=1000,generations=3000,genes=37,
                init_sd=.1,mutation_sd=.1,numpy=np.__version__,numba=numba.__version__,max_workers=2,threads_per_worker=3)
    save_json(out/'FREEZE.json',freeze)
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(worker,seed,name,str(out)) for seed in SEEDS for name in MODES]
        for future in concurrent.futures.as_completed(jobs):
            row=future.result();rows.append(row);print('V175_FINISHED',row,flush=True)
    tests={}
    for seed in SEEDS:
        q={r['mode']:r['Q_tail'] for r in rows if r['seed']==seed}
        hashes={r['initial_genotype_sha256'] for r in rows if r['seed']==seed};assert len(hashes)==1
        tests[str(seed)]=dict(Q=q,memory_gain=q['RNN_RESOURCE']-q['MLP_RESOURCE'],
                generic_memory_capacity=q['RNN_RESOURCE']>=.70,
                generic_memory_gain=q['RNN_RESOURCE']-q['MLP_RESOURCE']>=.15,
                diagnostic_full_rnn_capacity=q['RNN_FULL']>=.70,
                diagnostic_full_linear_capacity=q['LINEAR_FULL']>=.70,
                structured_filter_capacity=q['FILTER_RESOURCE']>=.70)
    save_json(out/'SUMMARY.json',dict(freeze=freeze,results=rows,tests=tests,
                                     external_replication=False,N2=0,scientific_novelty_not_accredited=True))
    print('V175_DONE',tests,flush=True)


if __name__=='__main__':main()
