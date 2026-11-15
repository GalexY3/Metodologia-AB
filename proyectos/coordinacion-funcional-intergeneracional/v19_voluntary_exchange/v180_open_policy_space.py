"""Formation versus maintenance and held-out affine invasion incentives."""
import os
os.environ.setdefault('NUMBA_NUM_THREADS','3')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse
import concurrent.futures
import hashlib
import inspect
import ast
import importlib.util
import json
from pathlib import Path
import time
import numpy as np
from research_resource_limits import apply_limits
from v178_private_affine_rival import generation,save

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/v180_open_policy_space'
GRID=(-1.,-.3,-.1,0.,.1,.3,1.)
CANDIDATES=[dict(family='BIAS',dS=0.,dA=0.,bias=b) for b in (-.1,-.03,-.01,-.003,0.,.003,.01,.03,.1,.3,1.)]
CANDIDATES += [dict(family='PLANE',dS=s,dA=a,bias=0.) for s in GRID for a in GRID]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def population(seed):
    p=ROOT/f'results/v178_private_affine_M5/FULL_{seed}/FINAL_POPULATION.npz'
    theta=np.load(p)['theta'].copy();theta[:,2]=0.
    return theta,p


def audit():
    limits=apply_limits(3);rng=np.random.default_rng(180900);rows=[]
    for m in (3,5,16):
        for positive in range(m+1):
            s=rng.uniform(-5,5,m);a=rng.uniform(-5,5,m)
            b=rng.uniform(.05,1,m);b[positive:]*=-1
            def step(state):
                x=state[0];y=state[1:]
                h=(x+s*m*y+a*y.sum()+b>0).astype(float)
                grown=x+(x-x*x)
                return np.r_[grown*(1-.9/m*h.sum()),.75*y+(.9/m)*h*grown]
            zero=np.zeros(m+1);eps=1e-8
            jac=np.column_stack([(step(np.eye(m+1)[i]*eps)-step(zero))/eps for i in range(m+1)])
            expected=np.zeros((m+1,m+1));expected[0,0]=2*(1-.9/m*positive)
            expected[1:,0]=2*(.9/m)*(b>0)
            expected[1:,1:]=np.eye(m)*.75
            err=float(np.max(abs(jac-expected)));assert err<3e-8,(m,positive,err)
            rows.append(dict(m=m,positive_intercepts=positive,max_error=err,
                resource_eigenvalue=float(expected[0,0]),stable_origin=bool(positive>m/1.8)))
    endpoints=[]
    for seed in range(178115,178123):
        th,p=population(seed);stored=np.load(p)
        fit=generation(th.reshape(100,5,3),stored['y0'],3)[0]
        err=float(np.max(abs(fit-stored['fit'])));assert err==0.,(seed,err)
        endpoints.append(dict(seed=seed,population_sha256=sha(p),max_error=err))
    return dict(limits=limits,source_sha256=sha(__file__),kernel_sha256=sha(ROOT/'v178_private_affine_rival.py'),
                original_endpoints=endpoints,boundary_jacobian=rows)


def warm_worker(seed,parent,arm):
    limits=apply_limits(3);path=OUT/f'maintenance/{arm}_{seed}';path.mkdir(parents=True,exist_ok=False)
    theta,p=population(parent);init=hashlib.sha256(theta.tobytes()).hexdigest()
    rng=np.random.default_rng([seed,100,5]);curve=[];start=time.perf_counter()
    mode=0 if arm=='LOCKED' else 3
    for g in range(3000):
        theta=theta[rng.permutation(500)];y0=(1+rng.normal(0,.1,(100,5)))/5
        fit,rates,resource,_,_=generation(theta.reshape(100,5,3),y0,mode)
        ind=fit.reshape(-1);total=ind.sum();assert np.isfinite(total) and total>0
        curve.append(dict(generation=g+1,Q=float(fit.sum(1).mean()),harvest=float(rates.mean()),
                          resource=float(resource.mean()),bias_positive=float(np.mean(theta[:,2]>0)),
                          bias_mean=float(theta[:,2].mean())))
        if g==2999:np.savez_compressed(path/'FINAL_POPULATION.npz',theta=theta,y0=y0,fit=fit)
        theta=theta[rng.choice(500,500,p=ind/total)]+rng.normal(0,.1,(500,3))
        if (g+1)%500==0:
            np.savez_compressed(path/f'CHECKPOINT_{g+1:04}.npz',theta_next=theta,curve_Q=np.array([r['Q'] for r in curve]))
            save(path/f'RNG_{g+1:04}.json',rng.bit_generator.state)
            with (path/'PROGRESS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(**curve[-1],elapsed=time.perf_counter()-start))+'\n')
    result=dict(seed=seed,parent=parent,arm=arm,Q_tail=float(np.mean([r['Q'] for r in curve[-500:]])),
                initial_genotype_sha256=init,parent_population_sha256=sha(p),limits=limits,
                elapsed=time.perf_counter()-start,generations=3000)
    save(path/'CURVE.json',curve);save(path/'RESULT.json',result);return result


def frozen_payoffs(parent,batches,candidates,subdir):
    th,pp=population(parent);records=[];fits=[]
    for batch in batches:
        rng=np.random.default_rng([batch,parent,5]);idx=rng.integers(0,500,(128,5));theta=th[idx]
        y0=(1+rng.normal(0,.1,(128,5)))/5
        base=generation(theta,y0,3)[0]
        mutant=[]
        for cand in candidates:
            tt=theta.copy();tt[:,0,0]+=cand['dS'];tt[:,0,1]+=cand['dA'];tt[:,0,2]=cand['bias']
            mutant.append(generation(tt,y0,3)[0])
        fits.append(np.stack([base]+mutant,axis=1))
    table=np.concatenate(fits)
    folder=OUT/subdir;folder.mkdir(exist_ok=True)
    np.savez_compressed(folder/f'PAYOFFS_{parent}.npz',fit=table)
    for j,cand in enumerate(candidates):
        records.append(dict(**cand,parent=parent,groups=len(table),
                  private_gain=float(np.mean(table[:,j+1,0]-table[:,0,0])),
                  group_gain=float(np.mean(table[:,j+1,:].sum(1)-table[:,0,:].sum(1))),
                  private_gain_fraction=float(np.mean(table[:,j+1,0]>table[:,0,0]+1e-10))))
    return records


def screen():
    rows=[]
    for parent in range(178115,178119):
        rows+=frozen_payoffs(parent,range(180315,180319),CANDIDATES,'screen')
        print('V180_SCREENED',parent,flush=True)
    selected=[]
    for family in ('BIAS','PLANE'):
        candidates=[c for c in CANDIDATES if c['family']==family];scored=[]
        for i,c in enumerate(candidates):
            found=[r for r in rows if all(r[k]==c[k] for k in ('family','dS','dA','bias'))]
            assert len(found)==4
            minimum=min(r['private_gain'] for r in found)
            norm=sum(c[k]**2 for k in ('dS','dA','bias'))**.5
            scored.append((minimum,-norm,-i,c))
        best=max(scored,key=lambda r:r[:3])
        selected.append(dict(**best[3],screen_minimum_private_gain=best[0]))
    save(OUT/'SCREEN.json',dict(candidates=CANDIDATES,results=rows))
    save(OUT/'SELECTION.json',dict(selected=selected,source_sha256=sha(__file__),
                screening_populations=list(range(178115,178119)),validation_not_yet_executed=True))
    return selected


def original_affine():
    p=ROOT/'literatura/original_code/Itao_ds_game_multi_player.py'
    spec=importlib.util.spec_from_file_location('v180_original_parity',p);src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
    tree=ast.parse(inspect.getsource(src.play_generation));count=0
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='z' for t in node.targets):
            node.value=ast.BinOp(left=node.value,op=ast.Add(),right=ast.Name(id='V180_BIAS',ctx=ast.Load()));count+=1
    assert count==1,count
    ast.fix_missing_locations(tree);scope=src.__dict__.copy();scope['V180_BIAS']=np.zeros((128,5))
    exec(compile(tree,'<v180_single_score_intercept>','exec'),scope)
    return scope,dict(original_sha256=sha(p),ast_sha256=hashlib.sha256(ast.dump(tree).encode()).hexdigest(),score_changes=count)


def validate(selection_commit):
    selection=json.loads((OUT/'SELECTION.json').read_text());candidates=[{k:c[k] for k in ('family','dS','dA','bias')} for c in selection['selected']]
    path=OUT/'VALIDATION.json';assert not path.exists();rows=[];parity=[]
    scope,provenance=original_affine()
    for parent in range(178119,178123):
        rows+=frozen_payoffs(parent,range(180415,180419),candidates,'validation')
        # External author's unmodified physics, with an audited score-only extension.
        th,_=population(parent);rng=np.random.default_rng([180415,parent,5]);idx=rng.integers(0,500,(128,5))
        theta=th[idx];y0=(1+rng.normal(0,.1,(128,5)))/5
        for c in candidates:
            tt=theta.copy();tt[:,0,0]+=c['dS'];tt[:,0,1]+=c['dA'];tt[:,0,2]=c['bias']
            scope['V180_BIAS'][:]=tt[:,:,2]
            ref=scope['play_generation'](tt[:,:,0],tt[:,:,1],rng,num_steps=1000,y0=y0,record_groups=128,record_steps=1000)
            got=generation(tt,y0,3,1000,True)
            err=float(np.max(abs(got[0]-ref['fit'])));mismatch=int(np.sum(got[3]!=ref['trace']['h']))
            assert err<1e-12 and mismatch==0,(parent,c,err,mismatch)
            parity.append(dict(parent=parent,family=c['family'],fitness_error=err,action_mismatches=mismatch))
        print('V180_VALIDATED',parent,flush=True)
    bias=[r for r in rows if r['family']=='BIAS']
    save(path,dict(selection_commit=selection_commit,selection_sha256=sha(OUT/'SELECTION.json'),
                results=rows,destructive_bias_in_all4=all(r['private_gain']>=.01 and r['group_gain']<=-.05 for r in bias),
                original_source_parity=parity,source_extension=provenance,
                independent_scientific_confirmation=False,CT2=61,N2=0))


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=('audit','maintenance-screen','validate'),required=True)
    p.add_argument('--prereg-commit');p.add_argument('--selection-commit');args=p.parse_args();limits=apply_limits(3)
    if args.stage=='audit':
        target=ROOT/'results/V180_PRE_RUN_AUDIT.json';assert not target.exists();result=audit();save(target,result);print('V180_AUDIT',json.dumps(result),flush=True);return
    pre=json.loads((ROOT/'results/V180_PRE_RUN_AUDIT.json').read_text());assert pre['source_sha256']==sha(__file__)
    if args.stage=='validate':
        assert args.selection_commit and len(args.selection_commit)==40
        validate(args.selection_commit);return
    assert args.prereg_commit and len(args.prereg_commit)==40;OUT.mkdir(exist_ok=False)
    save(OUT/'FREEZE.json',dict(prereg_commit=args.prereg_commit,source_sha256=sha(__file__),
              protocol_sha256=sha(ROOT/'PREREG_V180_OPEN_POLICY_SPACE.md'),audit=pre,limits=limits))
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(warm_worker,seed,parent,arm) for seed,parent in zip(range(180115,180123),range(178115,178123)) for arm in ('LOCKED','OPEN')]
        for future in concurrent.futures.as_completed(jobs):
            row=future.result();results.append(row);print('V180_MAINTENANCE',json.dumps(row),flush=True)
    paired=[]
    for seed in range(180115,180123):
        rr=[r for r in results if r['seed']==seed];assert len({r['initial_genotype_sha256'] for r in rr})==1
        q={r['arm']:r['Q_tail'] for r in rr}
        paired.append(dict(seed=seed,Q=q,difference=q['LOCKED']-q['OPEN'],loss=q['OPEN']<.3 and q['LOCKED']-q['OPEN']>=.5))
    save(OUT/'MAINTENANCE.json',dict(results=results,paired=paired,
                primary_gate=sum(r['loss'] for r in paired)>=6,
                control_gate=sum(r['Q']['LOCKED']>=.7 for r in paired)>=6))
    selected=screen();print('V180_SELECTION',json.dumps(selected),flush=True)
    print('V180_AWAITING_REMOTE_SELECTION_FREEZE',flush=True)


if __name__=='__main__':main()
