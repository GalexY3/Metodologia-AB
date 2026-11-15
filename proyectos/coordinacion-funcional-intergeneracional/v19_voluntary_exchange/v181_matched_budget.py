"""Matched total generations and a bias-reset control after V180."""
import os
os.environ.setdefault('NUMBA_NUM_THREADS','3')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from research_resource_limits import apply_limits
from v178_private_affine_rival import generation,save

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/v181_matched_budget'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source(parent,mode):
    p=ROOT/f'results/v178_private_affine_M5/{mode}_{parent}/FINAL_POPULATION.npz'
    return np.load(p)['theta'].copy(),p


def audit():
    limits=apply_limits(3);rows=[]
    assert sha(ROOT/'v178_private_affine_rival.py')=='83fb5177ef778cf5407bd5a7caa1753ca9cf9403d38383a671e098bba1051a96'
    for seed,parent in zip(range(180115,180123),range(178115,178123)):
        full,p=source(parent,'FULL');affine,a=source(parent,'AFFINE_FULL')
        reset=affine.copy();reset[:,2]=0.
        assert np.array_equal(reset[:,:2],affine[:,:2]) and np.all(reset[:,2]==0)
        full[:,2]=0.;rng=np.random.default_rng([seed,100,5])
        full=full[rng.permutation(500)];y0=(1+rng.normal(0,.1,(100,5)))/5
        q=float(generation(full.reshape(100,5,3),y0,3)[0].sum(1).mean())
        old=json.loads((ROOT/f'results/v180_open_policy_space/maintenance/OPEN_{seed}/CURVE.json').read_text())[0]['Q']
        assert q==old,(seed,q,old)
        rows.append(dict(seed=seed,parent=parent,full_source_sha256=sha(p),affine_source_sha256=sha(a),first_warm_generation_exact=True))
    return dict(source_sha256=sha(__file__),kernel_sha256=sha(ROOT/'v178_private_affine_rival.py'),checks=rows,limits=limits)


def worker(seed,parent,arm):
    limits=apply_limits(3);theta,p=source(parent,'AFFINE_FULL')
    if arm=='RESET_BIAS':theta[:,2]=0.
    init=hashlib.sha256(theta.tobytes()).hexdigest();path=OUT/f'{arm}_{seed}';path.mkdir(exist_ok=False)
    rng=np.random.default_rng([seed,100,5]);curve=[];start=time.perf_counter()
    for g in range(3000):
        theta=theta[rng.permutation(500)];y0=(1+rng.normal(0,.1,(100,5)))/5
        fit,rates,resource,_,_=generation(theta.reshape(100,5,3),y0,3)
        ind=fit.reshape(-1);total=ind.sum();assert np.isfinite(total) and total>0
        curve.append(dict(generation=g+1,total_generations=3001+g,Q=float(fit.sum(1).mean()),
                          harvest=float(rates.mean()),resource=float(resource.mean()),bias_mean=float(theta[:,2].mean())))
        if g==2999:np.savez_compressed(path/'FINAL_POPULATION.npz',theta=theta,y0=y0,fit=fit)
        theta=theta[rng.choice(500,500,p=ind/total)]+rng.normal(0,.1,(500,3))
        if (g+1)%500==0:
            np.savez_compressed(path/f'CHECKPOINT_{g+1:04}.npz',theta_next=theta,curve_Q=np.array([r['Q'] for r in curve]))
            save(path/f'RNG_{g+1:04}.json',rng.bit_generator.state)
            with (path/'PROGRESS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(**curve[-1],elapsed=time.perf_counter()-start))+'\n')
    result=dict(seed=seed,parent=parent,arm=arm,Q_tail=float(np.mean([r['Q'] for r in curve[-500:]])),
                initial_genotype_sha256=init,parent_source_sha256=sha(p),limits=limits,
                continuation_generations=3000,total_generations=6000,elapsed=time.perf_counter()-start)
    save(path/'CURVE.json',curve);save(path/'RESULT.json',result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit-only',action='store_true');p.add_argument('--prereg-commit');args=p.parse_args()
    if args.audit_only:
        path=ROOT/'results/V181_PRE_RUN_AUDIT.json';assert not path.exists();a=audit();save(path,a);print('V181_AUDIT',json.dumps(a),flush=True);return
    assert args.prereg_commit and len(args.prereg_commit)==40
    pre=json.loads((ROOT/'results/V181_PRE_RUN_AUDIT.json').read_text());assert pre['source_sha256']==sha(__file__)
    OUT.mkdir(exist_ok=False);save(OUT/'FREEZE.json',dict(prereg_commit=args.prereg_commit,source_sha256=sha(__file__),
                 protocol_sha256=sha(ROOT/'PREREG_V181_MATCHED_BUDGET_AND_BIAS_RESET.md'),audit=pre,
                 previous_control='results/v180_open_policy_space/MAINTENANCE.json',max_workers=2,threads_per_worker=3))
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(worker,seed,parent,arm) for seed,parent in zip(range(180115,180123),range(178115,178123)) for arm in ('CONTINUE','RESET_BIAS')]
        for future in concurrent.futures.as_completed(jobs):
            row=future.result();results.append(row);print('V181_FINISHED',json.dumps(row),flush=True)
    old=json.loads((ROOT/'results/v180_open_policy_space/MAINTENANCE.json').read_text());paired=[]
    for seed in range(180115,180123):
        q={r['arm']:r['Q_tail'] for r in results if r['seed']==seed}
        warm=next(r['Q']['OPEN'] for r in old['paired'] if r['seed']==seed)
        paired.append(dict(seed=seed,warm=warm,continue_affine=q['CONTINUE'],reset_bias=q['RESET_BIAS'],
                warm_minus_continue=warm-q['CONTINUE'],warm_minus_reset=warm-q['RESET_BIAS']))
    checks={arm:dict(median_advantage=float(np.median([r[key] for r in paired])),
            positive_pairs=sum(r[key]>0 for r in paired)) for arm,key in (('CONTINUE','warm_minus_continue'),('RESET_BIAS','warm_minus_reset'))}
    primary=all(r['median_advantage']>=.2 and r['positive_pairs']>=6 for r in checks.values())
    save(OUT/'SUMMARY.json',dict(results=results,paired=paired,tests=checks,primary_gate=bool(primary),
          control_reused_not_new_sample=True,paired_histories=8,additional_continuations=16,
          external_confirmation=False,CT2_historical=61,N2=0))
    print('V181_DONE',json.dumps(dict(paired=paired,tests=checks,primary_gate=primary)),flush=True)


if __name__=='__main__':main()
