"""Two privately trained neural payoff estimators with local held-out inputs.

Full-information and importance-weighted bandit regression have equal expected
gradients, conditional on the other agent's action. Feedback richness is imposed,
not a learned institution. The oracle condition is an external positive control.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from pathlib import Path
import argparse
import copy
import hashlib
import json
import time
import numpy as np
import torch
from torch import nn
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver,extract_optimizer
from v191_dual_neural_credit import P,N,EPS,SEEDS,sample_action,sampling_probability,full_loss,bandit_loss,environment_feedback,joint_accuracy

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V192_DUAL_NEURAL_LEARNING'
STEPS=60000


def contexts():
    data=[np.load(BASE/f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz') for seed in SEEDS]
    return {key:np.stack([d[key] for d in data]) for key in ['masks','a','b','f']}


@torch.no_grad()
def evaluate(models,data,device):
    aa,bb=np.indices((P,P));truth=((aa+bb)%P).ravel()
    n=len(SEEDS)
    ia=torch.tensor(aa.ravel(),device=device)[None].expand(n,-1)
    ib=torch.tensor(bb.ravel(),device=device)[None].expand(n,-1)
    prediction=[model(ia,ib).argmax(2).cpu().numpy() for model in models]
    rows=[]
    for s in range(n):
        hist=[]
        for role in range(2):
            error=(prediction[role][s]-truth)%P;mask=data['masks'][s,role].ravel()
            hist.append([np.bincount(error[part],minlength=P)/int(part.sum()) for part in [mask,~mask]])
        gauge=int(hist[0][0].argmax());opposite=(-gauge)%P
        row=dict(train_joint_greedy=joint_accuracy(hist[0][0],hist[1][0]),
                 test_joint_greedy=joint_accuracy(hist[0][1],hist[1][1]),
                 train_A=float(hist[0][0][gauge]),train_B=float(hist[1][0][opposite]),
                 test_A=float(hist[0][1][gauge]),test_B=float(hist[1][1][opposite]),
                 train_chosen_gauge_A=gauge,train_chosen_gauge_B=opposite,
                 independently_modal_gauge_B=int(hist[1][0].argmax()),
                 train_joint_behavior_expected=joint_accuracy((1-EPS)*hist[0][0]+EPS/P,(1-EPS)*hist[1][0]+EPS/P),
                 test_joint_behavior_expected=joint_accuracy((1-EPS)*hist[0][1]+EPS/P,(1-EPS)*hist[1][1]+EPS/P),
                 train_feedback_identifiability_gap_A=float(np.sort(hist[1][0])[-1]-np.sort(hist[1][0])[-2]),
                 train_feedback_identifiability_gap_B=float(np.sort(hist[0][0])[-1]-np.sort(hist[0][0])[-2]),
                 train_error_histograms=[hist[r][0].tolist() for r in range(2)],
                 test_error_histograms=[hist[r][1].tolist() for r in range(2)])
        rows.append(row)
    return rows


def snapshot(models,optimizers,rngs,s,step,history,seed,family):
    return dict(seed=seed,family=family,step=step,
                models=[{k:v[s:s+1].detach().clone() for k,v in model.state_dict().items()} for model in models],
                optimizers=[extract_optimizer(opt,s) for opt in optimizers],
                rng_state=copy.deepcopy(rngs[s].bit_generator.state),history=copy.deepcopy(history),
                checkpoint_selected_by_training_only=True)


def train(family):
    folder=OUT/family;folder.mkdir(exist_ok=False)
    data=contexts();device='cuda';n=len(SEEDS)
    models=[BatchedReceiver([2*seed+role for seed in SEEDS],device=device) for role in range(2)]
    optimizers=[torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98)) for model in models]
    a,b,f=[torch.tensor(data[key],device=device,dtype=torch.long) for key in ['a','b','f']]
    fa,fb=f[:,0],f[:,1]
    rngs=[np.random.default_rng(seed+10000) for seed in SEEDS]
    histories=[[] for _ in SEEDS];mem_streak=[0]*n;gen_streak=[0]*n;t_mem=[None]*n;t_gen=[None]*n
    started=time.monotonic();block=started
    for step in range(1,STEPS+1):
        draws=[r.random((2,N)) for r in rngs]
        coins=torch.tensor(np.stack(draws),device=device)
        permutation=torch.tensor(np.stack([r.permutation(N) for r in rngs]),device=device)
        values=[models[role](a[:,role],b[:,role]) for role in range(2)]
        greedy=[v.detach().argmax(2) for v in values]
        actions=[sample_action(greedy[role],coins[:,role]) for role in range(2)]
        if family=='PRIVATE_BANDIT_IS':
            # The learner never receives a counterfactual vector or local f.
            world_target=(fa+fb.gather(1,permutation))%P
            ra=(((actions[0]+actions[1].gather(1,permutation))%P)==world_target).float()
            rb=torch.zeros_like(ra).scatter(1,permutation,ra)
            rewards=[ra,rb]
            losses=[bandit_loss(values[role],actions[role],rewards[role],
                                sampling_probability(actions[role],greedy[role])) for role in range(2)]
        else:
            partner_actions=actions
            if family=='ORACLE_FULL':
                # Positive control: virtual partners already know f, with the
                # same exploration law. These conventions are supplied.
                partner_actions=[sample_action(f[:,role],coins[:,role]) for role in range(2)]
            pa,pb,_,_=environment_feedback(fa,fb,partner_actions[0],partner_actions[1],permutation)
            payoffs=[pa,pb]
            rewards=[payoffs[role].gather(2,actions[role][:,:,None]).squeeze(2) for role in range(2)]
            losses=[full_loss(values[role],payoffs[role]) for role in range(2)]
        # Models have separate parameters and optimizers. Both payoffs were
        # computed from pre-update actions; updating A cannot differentiate B.
        for role in range(2):
            optimizers[role].zero_grad(set_to_none=True);losses[role].backward();optimizers[role].step()
        if step%100==0:
            rows=evaluate(models,data,device)
            for s,row in enumerate(rows):
                row['step']=step;histories[s].append(row)
                mem_streak[s]=mem_streak[s]+1 if row['train_joint_greedy']>=.99 else 0
                gen_streak[s]=gen_streak[s]+1 if row['test_joint_greedy']>=.95 else 0
                if t_mem[s] is None and mem_streak[s]>=5:
                    t_mem[s]=step
                    torch.save(snapshot(models,optimizers,rngs,s,step,histories[s],SEEDS[s],family),folder/f'first_memorization_s{SEEDS[s]}.pt')
                if t_gen[s] is None and gen_streak[s]>=5:t_gen[s]=step
            if step%1000==0:
                print('V192',family,step,'train',round(np.mean([r['train_joint_greedy'] for r in rows]),4),
                      'test',round(np.mean([r['test_joint_greedy'] for r in rows]),4),
                      'mem',sum(t is not None for t in t_mem),'sec',round(time.monotonic()-started,1),flush=True)
            if step%5000==0:
                torch.save(dict(models=[m.state_dict() for m in models],optimizers=[o.state_dict() for o in optimizers],
                                step=step,rng_states=[r.bit_generator.state for r in rngs],histories=histories),folder/f'checkpoint_{step}.pt')
                (folder/'progress.json').write_text(json.dumps(dict(step=step,rows=rows),indent=2),encoding='utf-8')
            time.sleep(max(0.,.4-(time.monotonic()-block)));block=time.monotonic()
    results=[]
    for s,seed in enumerate(SEEDS):
        final=histories[s][-1];tm=t_mem[s];tg=t_gen[s]
        delayed=tm is not None and tg is not None and tg>=5*tm and tg-tm>=2000 and final['train_joint_greedy']>=.99 and final['test_joint_greedy']>=.95
        result=dict(seed=seed,family=family,final=final,history=histories[s],t_mem=tm,t_gen=tg,
                    delayed_joint_generalization_candidate=bool(delayed),
                    multiple_neural_agents=True,ongoing_coadaptation_necessity_not_tested=True)
        (folder/f'metrics_s{seed}.json').write_text(json.dumps(result,indent=2),encoding='utf-8');results.append(result)
    del models,optimizers;torch.cuda.empty_cache()
    return results


def run():
    receipt=json.loads((BASE/'results/V192_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_training'] and receipt['remote_commit']
    for path,sha in receipt['source_sha256'].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==sha,path
    assert not json.loads((BASE/'results/V191_TECHNICAL_AUDIT.json').read_text(encoding='utf-8'))['failures']
    OUT.mkdir(exist_ok=False);torch.cuda.set_per_process_memory_fraction(.35)
    (OUT/'MANIFEST.json').write_text(json.dumps(dict(preregistration=receipt,torch=torch.__version__,device=torch.cuda.get_device_name(),
        private_agent_pairs_per_method=4,local_neural_learners_per_pair=2,shared_parameters=False,
        counterfactual_feedback_externally_supplied=True,epsilon=EPS,
        task_and_common_interests_programmed=True),indent=2),encoding='utf-8')
    results=train('ORACLE_FULL')
    control=sum(r['final']['test_joint_greedy']>=.95 for r in results)
    cancelled=[]
    if control>=3:
        for family in ['PRIVATE_FULL','PRIVATE_BANDIT_IS']:results.extend(train(family))
    else:cancelled=['PRIVATE_FULL','PRIVATE_BANDIT_IS']
    counts={family:sum(r['delayed_joint_generalization_candidate'] for r in results if r['family']==family)
            for family in ['ORACLE_FULL','PRIVATE_FULL','PRIVATE_BANDIT_IS'] if any(r['family']==family for r in results)}
    full=[r for r in results if r['family']=='PRIVATE_FULL'];bandit=[r for r in results if r['family']=='PRIVATE_BANDIT_IS']
    advantage=[x['final']['test_joint_greedy']-y['final']['test_joint_greedy'] for x,y in zip(full,bandit)]
    contrast=bool(len(full)==4 and sum(r['final']['test_joint_greedy']>=.95 for r in full)>=3 and np.median(advantage)>=.1)
    summary=dict(runs=[{k:v for k,v in r.items() if k!='history'} for r in results],positive_control_count=control,
                 control_gate_passed=control>=3,cancelled_unexecuted_conditions=cancelled,
                 delayed_candidate_counts=counts,robust_full_private_delayed_candidate=counts.get('PRIVATE_FULL',0)>=3,
                 full_minus_bandit_test=advantage,credit_contrast_passed=contrast,
                 collective_grokking_causally_accredited=False,institution_learning_accredited=False,
                 CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('V192_COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='runs'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run']);p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;run()
