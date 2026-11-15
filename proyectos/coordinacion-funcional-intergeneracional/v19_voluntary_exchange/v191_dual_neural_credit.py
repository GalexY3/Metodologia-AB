"""Dual neural one-stage game: private feedback and exact estimator audits.

No novelty is claimed for importance sampling, marginalization or coordination.
Neither agent receives its own local ground-truth sum during private training.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from pathlib import Path
import itertools
import json
import numpy as np
import torch
from torch import nn
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V191_DUAL_NEURAL_AUDIT_V2'
P=31;N=384;EPS=.1
SEEDS=list(range(192115,192119))


def sample_action(greedy,coin,p=P,epsilon=EPS):
    return torch.where(coin<epsilon,(coin/epsilon*p).long(),greedy)


def sampling_probability(action,greedy,p=P,epsilon=EPS):
    return epsilon/p+(1-epsilon)*(action==greedy).to(torch.float64)


def full_loss(values,own_payoffs):
    return (values-own_payoffs).square().mean((1,2)).sum()


def bandit_loss(values,own_action,own_reward,own_sampling_probability,p=P):
    # Own sampling probability is detached: this is payoff regression, not a
    # policy-gradient derivative through the sampling mechanism.
    q=own_sampling_probability.detach().to(values.dtype)
    selected=values.gather(2,own_action[:,:,None]).squeeze(2)
    return ((selected-own_reward).square()/(p*q)).mean(1).sum()


def environment_feedback(fa,fb,action_a,action_b,permutation,p=P):
    """Environment knows the world; learner loss functions receive own fields."""
    joint_target=(fa+fb.gather(1,permutation))%p
    target_a=(joint_target-action_b.gather(1,permutation))%p
    target_b=torch.zeros_like(target_a).scatter(1,permutation,(joint_target-action_a)%p)
    pay_a=nn.functional.one_hot(target_a,p).to(torch.float32)
    pay_b=nn.functional.one_hot(target_b,p).to(torch.float32)
    reward_a=pay_a.gather(2,action_a[:,:,None]).squeeze(2)
    reward_b=pay_b.gather(2,action_b[:,:,None]).squeeze(2)
    return pay_a,pay_b,reward_a,reward_b


def joint_accuracy(hist_a,hist_b):
    return float(np.dot(hist_a,hist_b[(-np.arange(len(hist_b)))%len(hist_b)]))


def make_contexts():
    pairs=np.array(list(itertools.combinations(range(P),2)))
    aa,bb=np.indices((P,P));truth=(aa+bb)%P
    records=[]
    for s,seed in enumerate(SEEDS):
        masks=[];xa=[];xb=[];ff=[]
        for role in range(2):
            context_seed=192000+2*s+role
            rng=np.random.default_rng(context_seed)
            for attempt in range(100):
                chosen=rng.choice(len(pairs),N//2,replace=False)
                mask=np.zeros((P,P),dtype=bool)
                for a,b in pairs[chosen]:mask[a,b]=mask[b,a]=True
                assert mask.sum()==N and np.array_equal(mask,mask.T) and not np.any(mask.diagonal())
                if set(aa[mask])==set(range(P)) and set(bb[mask])==set(range(P)) and set(truth[mask])==set(range(P)):break
                excluded=OUT/f'excluded_context_{context_seed}_attempt{attempt}.npz'
                if excluded.exists():assert np.array_equal(np.load(excluded)['mask'],mask)
                else:np.savez_compressed(excluded,mask=mask)
            else:raise RuntimeError('No full-marginal context in fixed attempt budget')
            masks.append(mask);xa.append(aa[mask]);xb.append(bb[mask]);ff.append(truth[mask])
        path=OUT/f'context_s{seed}.npz'
        arrays=dict(masks=np.stack(masks),a=np.stack(xa),b=np.stack(xb),f=np.stack(ff))
        if path.exists():
            previous=np.load(path)
            for key,value in arrays.items():assert np.array_equal(previous[key],value)
        else:np.savez_compressed(path,**arrays)
        records.append(dict(seed=seed,context_seeds=[192000+2*s,192001+2*s],
                            local_train=384,local_test=577,all_marginals_seen=True,
                            reversed_pair_leakage=False,diagonal_pairs_always_held_out=True))
    return records


def technical():
    OUT.mkdir(exist_ok=True)
    contexts=make_contexts();checks=[]
    rng=np.random.default_rng(191900)
    for fixture in range(6):
        p=7;n=11
        values=torch.tensor(rng.normal(size=(2,n,p)),dtype=torch.float64,requires_grad=True)
        labels=torch.tensor(rng.integers(p,size=(2,n)))
        payoff=nn.functional.one_hot(labels,p).double()
        greedy=values.detach().argmax(2)
        dense=full_loss(values,payoff)
        dense_grad=torch.autograd.grad(dense,values,retain_graph=True)[0]
        sampled=torch.tensor(rng.integers(p,size=(2,n)))
        sampled_q=sampling_probability(sampled,greedy,p)
        sampled_reward=(sampled==labels).double()
        actual_bandit=bandit_loss(values,sampled,sampled_reward,sampled_q,p)
        selected=values.gather(2,sampled[:,:,None]).squeeze(2)
        reference_bandit=((selected-sampled_reward).square()/(p*sampled_q)).mean(1).sum()
        assert abs(float(actual_bandit.detach()-reference_bandit.detach()))<1e-12
        # Exactly integrate the bandit loss/gradient, with feedback for each
        # action. No Monte Carlo tolerance is used in this identity check.
        integrated=torch.zeros((),dtype=torch.float64)
        for action in range(p):
            a=torch.full_like(labels,action)
            q=sampling_probability(a,greedy,p)
            reward=(labels==action).double()
            selected=values[:,:,action]
            integrated+=((q*((selected-reward).square()/(p*q))).mean(1)).sum()
        grad=torch.autograd.grad(integrated,values)[0]
        for name,error in [('loss_unbiased',abs(float(integrated.detach()-dense.detach()))),
                           ('gradient_unbiased',float((grad-dense_grad).abs().max()))]:
            checks.append(dict(fixture=fixture,check=name,error=float(error),tolerance=1e-12,passed=bool(error<1e-12)))
        fa=torch.tensor(rng.integers(p,size=(2,n)));fb=torch.tensor(rng.integers(p,size=(2,n)))
        a=torch.tensor(rng.integers(p,size=(2,n)));b=torch.tensor(rng.integers(p,size=(2,n)))
        permutation=torch.tensor(np.stack([rng.permutation(n) for _ in range(2)]))
        pa,pb,ra,rb=environment_feedback(fa,fb,a,b,permutation,p)
        for s in range(2):
            for i in range(n):
                j=int(permutation[s,i]);target=int((fa[s,i]+fb[s,j])%p)
                for u in range(p):
                    assert float(pa[s,i,u])==float((u+int(b[s,j]))%p==target)
                    assert float(pb[s,j,u])==float((int(a[s,i])+u)%p==target)
                assert ra[s,i]==rb[s,j]
        # Stochastic identity checked by explicit independent enumeration over
        # states and actions, versus a distribution of modular errors.
        pi_a=rng.random((n,p));pi_a/=pi_a.sum(1,keepdims=True)
        pi_b=rng.random((n,p));pi_b/=pi_b.sum(1,keepdims=True)
        h1=np.zeros(p);h2=np.zeros(p);brute=0.
        for i in range(n):
            for u in range(p):
                h1[(u-int(fa[0,i]))%p]+=pi_a[i,u]/n
                h2[(u-int(fb[0,i]))%p]+=pi_b[i,u]/n
                for j in range(n):
                    for v in range(p):
                        brute+=pi_a[i,u]*pi_b[j,v]*float((u+v-int(fa[0,i])-int(fb[0,j]))%p==0)/(n*n)
        error=abs(brute-joint_accuracy(h1,h2))
        checks.append(dict(fixture=fixture,check='joint_accuracy_factorization',error=float(error),tolerance=1e-12,passed=bool(error<1e-12)))
    # Separate networks; feedback action indices carry no autograd connection.
    first=BatchedReceiver([191901],dtype=torch.float64)
    second=BatchedReceiver([191902],dtype=torch.float64)
    ia=torch.arange(17)[None]%P;ib=(ia*3)%P
    qa=first(ia,ib);qb=second(ia,ib)
    own_payoff=nn.functional.one_hot((qb.detach().argmax(2)+3)%P,P).double()
    full_loss(qa,own_payoff).backward()
    assert any(p.grad is not None and p.grad.abs().sum()>0 for p in first.parameters())
    assert all(p.grad is None for p in second.parameters())
    failures=[r for r in checks if not r['passed']]
    coins=(torch.arange(7000,dtype=torch.float64)+.5)/7000
    actions=sample_action(torch.full((7000,),2),coins,p=7)
    empirical=torch.bincount(actions,minlength=7).double()/7000
    expected=torch.full((7,),.1/7,dtype=torch.float64);expected[2]+=.9
    assert float((empirical-expected).abs().max())<1e-12
    result=dict(checks=checks,failures=failures,contexts=contexts,
                feedback_table_entries_checked=6*2*11*7*2,
                equal_expected_loss_and_gradient_verified=True,
                private_network_gradients_isolated=True,
                action_sampler_epsilon_greedy=True,
                bandit_loss_has_no_counterfactual_or_local_truth_input=True,
                neural_training_executed=False,known_identities_not_originality=True)
    output=BASE/'results/V191_TECHNICAL_AUDIT.json';assert not output.exists()
    serialized=json.dumps(result,indent=2)
    output.write_text(serialized,encoding='utf-8')
    assert not failures
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','contexts']}),flush=True)


if __name__=='__main__':print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);technical()
