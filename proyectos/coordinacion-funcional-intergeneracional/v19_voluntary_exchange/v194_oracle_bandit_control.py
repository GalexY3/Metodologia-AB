"""Capability control: binary-feedback learner with already-correct partners.

This distinguishes endogenous peer-feedback failure from generic incapacity of
the importance-weighted bandit regressor. It is not a new learning algorithm.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
import torch
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver
from v191_dual_neural_credit import P,N,EPS,SEEDS,sample_action,sampling_probability,bandit_loss,environment_feedback
from v192_dual_neural_learning import contexts,evaluate,snapshot

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V194_ORACLE_BANDIT'
STEPS=60000


def own_rewards(fa,fb,own_a,own_b,oracle_a,oracle_b,permutation,p=P):
    world_target=(fa+fb.gather(1,permutation))%p
    reward_a=(((own_a+oracle_b.gather(1,permutation))%p)==world_target).float()
    reward_b=torch.zeros_like(reward_a).scatter(1,permutation,
        (((oracle_a+own_b.gather(1,permutation))%p)==world_target).float())
    return reward_a,reward_b


def technical():
    rng=np.random.default_rng(194900);entries=0
    for fixture in range(6):
        p=7;n=17
        tensors=[torch.tensor(rng.integers(p,size=(2,n))) for _ in range(6)]
        fa,fb,ua,ub,oa,ob=tensors
        perm=torch.tensor(np.stack([rng.permutation(n) for _ in range(2)]))
        ra,rb=own_rewards(fa,fb,ua,ub,oa,ob,perm,p)
        pa,pb,_,_=environment_feedback(fa,fb,oa,ob,perm,p)
        assert torch.equal(ra,pa.gather(2,ua[:,:,None]).squeeze(2))
        assert torch.equal(rb,pb.gather(2,ub[:,:,None]).squeeze(2))
        for s in range(2):
            for i in range(n):
                j=int(perm[s,i]);target=(int(fa[s,i])+int(fb[s,j]))%p
                assert float(ra[s,i])==float((int(ua[s,i])+int(ob[s,j]))%p==target)
                assert float(rb[s,j])==float((int(oa[s,i])+int(ub[s,j]))%p==target)
                entries+=2
    result=dict(explicit_reward_entries_checked=entries,conditional_payoff_table_agreement=True,
                bandit_expected_gradient_identity_reused_from_V191=True,failures=[],scientific_training_executed=False)
    output=BASE/'results/V194_TECHNICAL_AUDIT.json';assert not output.exists()
    output.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)


def run():
    receipt=json.loads((BASE/'results/V194_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path,sha in receipt['source_sha256'].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==sha,path
    OUT.mkdir(exist_ok=False);torch.cuda.set_per_process_memory_fraction(.35)
    (OUT/'MANIFEST.json').write_text(json.dumps(dict(preregistration=receipt,
        original_seed_blocks_reused=4,independent_new_roots=0,oracle_convention_supplied=True,
        scalar_reward_only_for_learners=True,torch=torch.__version__,device=torch.cuda.get_device_name()),indent=2),encoding='utf-8')
    data=contexts();device='cuda';n=len(SEEDS)
    a,b,f=[torch.tensor(data[k],device=device,dtype=torch.long) for k in ['a','b','f']]
    models=[BatchedReceiver([2*seed+role for seed in SEEDS],device=device) for role in range(2)]
    opts=[torch.optim.AdamW(m.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98)) for m in models]
    rngs=[np.random.default_rng(seed+10000) for seed in SEEDS]
    histories=[[] for _ in SEEDS];sm=[0]*n;sg=[0]*n;tm=[None]*n;tg=[None]*n
    started=time.monotonic();block=started
    for step in range(1,STEPS+1):
        coins=torch.tensor(np.stack([r.random((2,N)) for r in rngs]),device=device)
        perm=torch.tensor(np.stack([r.permutation(N) for r in rngs]),device=device)
        values=[models[role](a[:,role],b[:,role]) for role in range(2)]
        greedy=[v.detach().argmax(2) for v in values]
        actions=[sample_action(greedy[r],coins[:,r]) for r in range(2)]
        oracle=[sample_action(f[:,r],coins[:,r]) for r in range(2)]
        rewards=own_rewards(f[:,0],f[:,1],actions[0],actions[1],oracle[0],oracle[1],perm)
        losses=[bandit_loss(values[r],actions[r],rewards[r],sampling_probability(actions[r],greedy[r])) for r in range(2)]
        for r in range(2):opts[r].zero_grad(set_to_none=True);losses[r].backward();opts[r].step()
        if step%100==0:
            rows=evaluate(models,data,device)
            for s,row in enumerate(rows):
                row['step']=step;histories[s].append(row)
                sm[s]=sm[s]+1 if row['train_joint_greedy']>=.99 else 0
                sg[s]=sg[s]+1 if row['test_joint_greedy']>=.95 else 0
                if tm[s] is None and sm[s]>=5:
                    tm[s]=step
                    torch.save(snapshot(models,opts,rngs,s,step,histories[s],SEEDS[s],'ORACLE_BANDIT_IS'),OUT/f'first_memorization_s{SEEDS[s]}.pt')
                if tg[s] is None and sg[s]>=5:tg[s]=step
            if step%1000==0:print('V194',step,'train',round(np.mean([r['train_joint_greedy'] for r in rows]),4),
                                  'test',round(np.mean([r['test_joint_greedy'] for r in rows]),4),'sec',round(time.monotonic()-started,1),flush=True)
            if step%5000==0:
                torch.save(dict(models=[m.state_dict() for m in models],optimizers=[o.state_dict() for o in opts],step=step,
                    histories=histories,rng_states=[r.bit_generator.state for r in rngs]),OUT/f'checkpoint_{step}.pt')
                (OUT/'progress.json').write_text(json.dumps(dict(step=step,rows=rows),indent=2),encoding='utf-8')
            time.sleep(max(0.,.4-(time.monotonic()-block)));block=time.monotonic()
    results=[]
    for s,seed in enumerate(SEEDS):
        final=histories[s][-1]
        result=dict(seed=seed,family='ORACLE_BANDIT_IS',final=final,history=histories[s],t_mem=tm[s],t_gen=tg[s])
        (OUT/f'metrics_s{seed}.json').write_text(json.dumps(result,indent=2),encoding='utf-8');results.append(result)
    count=sum(r['final']['test_joint_greedy']>=.95 for r in results)
    summary=dict(runs=[{k:v for k,v in r.items() if k!='history'} for r in results],positive_control_count=count,
        bandit_component_competence_passed=count>=3,
        V192_bandit_failure_cannot_be_attributed_specifically_to_endogenous_peers=count<3,
        endogenous_cooperation_or_institution_accredited=False,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V194_COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='runs'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['technical','run']);a=p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False
    {'technical':technical,'run':run}[a.command]()
