"""Exact restricted gate game for previously evolved ecological policies."""
import os
os.environ.setdefault('NUMBA_NUM_THREADS','3')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from research_resource_limits import apply_limits
from v176_frozen_memory_causal import evaluate
from v175_memory_evolution import MODES,save_json

ROOT=Path(__file__).resolve().parent
NAMES=('RNN_FULL','RNN_RESOURCE','LINEAR_FULL')
SEEDS=(175115,175116)
BATCHES=tuple(range(177115,177119))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(commit):
    limits=apply_limits(3)
    assert sha(ROOT/'v176_frozen_memory_causal.py')=='f982ff043754723301a724d6c75bab617e30918f193a8d782864f076e3f848ad'
    out=ROOT/'results/v177_gate_game';out.mkdir(exist_ok=False)
    save_json(out/'FREEZE.json',dict(prereg_commit=commit,source_sha256=sha(__file__),
          protocol_sha256=sha(ROOT/'PREREG_V177_COGNITIVE_GATE_GAME.md'),limits=limits,
          source_population_prereg='e5dd0826c29f97d246d80d5a8e8f16072e56552b'))
    summaries=[]
    for seed in SEEDS:
        for name in NAMES:
            pp=ROOT/f'results/v175_learned_memory/{name}_{seed}/FINAL_POPULATION.npz'
            population=np.load(pp)['theta'];tables=[];indices=[];initial=[]
            for batch in BATCHES:
                rng=np.random.default_rng([batch,seed,5]);idx=rng.integers(0,500,(128,5))
                theta=population[idx];y0=(1+rng.normal(0,.1,(128,5)))/5
                pay=np.empty((128,32,5))
                for mask in range(32):
                    tt=theta.copy()
                    for i in range(5):
                        if not mask&(1<<i):tt[:,i,12:28]=0.
                    pay[:,mask,:]=evaluate(tt,y0,MODES[name],0)[0]
                reset=evaluate(theta,y0,MODES[name],1)[0]
                assert np.array_equal(pay[:,0,:],reset),(name,seed,batch,'zero recurrence/reset mismatch')
                if name=='LINEAR_FULL':assert np.array_equal(pay,np.repeat(pay[:,0:1,:],32,axis=1))
                tables.append(pay);indices.append(idx);initial.append(y0)
            pay=np.concatenate(tables);n=pay.shape[0];regret=np.zeros((n,32))
            for mask in range(32):
                gains=np.stack([pay[:,mask^(1<<i),i]-pay[:,mask,i] for i in range(5)],axis=1)
                regret[:,mask]=np.maximum(0,gains.max(1))
            nash=regret<=1e-10
            change=pay[:,0,:]-pay[:,31,:]
            pareto=(change.min(1)>=-1e-10)&(change.max(1)>1e-10)
            trap=nash[:,31]&pareto
            by_k=[]
            for k in range(5):
                masks=[mask for mask in range(0,32,2) if mask.bit_count()==k]
                delta=np.stack([pay[:,mask,0]-pay[:,mask|1,0] for mask in masks],axis=1)
                by_k.append(dict(other_active=k,off_minus_on=float(delta.mean()),
                         fraction_off_profitable=float(np.mean(delta>1e-10))))
            row=dict(seed=seed,mode=name,groups=n,population_sha256=sha(pp),
                Q_all_on=float(pay[:,31,:].sum(1).mean()),Q_all_off=float(pay[:,0,:].sum(1).mean()),
                all_on_restricted_nash=float(nash[:,31].mean()),all_off_restricted_nash=float(nash[:,0].mean()),
                all_off_pareto_improvement=float(pareto.mean()),strong_trap_fraction=float(trap.mean()),
                no_pure_restricted_nash=float(np.mean(nash.sum(1)==0)),
                unilateral_off_private_gain=float((pay[:,30,0]-pay[:,31,0]).mean()),
                unilateral_off_profitable_fraction=float(np.mean(pay[:,30,0]>pay[:,31,0]+1e-10)),
                all_on_regret_mean=float(regret[:,31].mean()),by_other_active=by_k)
            np.savez_compressed(out/f'{name}_{seed}_PAYOFFS.npz',payoffs=pay,regret=regret,
                                sampled_indices=np.concatenate(indices),initial_wealth=np.concatenate(initial))
            save_json(out/f'{name}_{seed}_SUMMARY.json',row);summaries.append(row)
            print('V177',json.dumps(row),flush=True)
    rr=[r for r in summaries if r['mode']=='RNN_FULL']
    save_json(out/'SUMMARY.json',dict(results=summaries,
          strong_collective_trap_in_both=all(r['strong_trap_fraction']>=.5 for r in rr),
          learned_institution=False,external_confirmation=False,CT2=61,N2=0))
    print('V177_DONE',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prereg-commit',required=True);args=p.parse_args()
    assert len(args.prereg_commit)==40
    run(args.prereg_commit)
