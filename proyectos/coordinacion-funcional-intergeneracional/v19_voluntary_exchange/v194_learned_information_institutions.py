"""V194. Independent private Q agents learn information regime and approval votes.
Cohort means aggregated by world. No roles, donations, institutions invented.
Preregistration PREREG_V194_PRIVATE_ENDOGENOUS_INFORMATION_VOTE.md.
"""
from __future__ import annotations
import argparse,hashlib,json,math,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
W=32; G=20
TRAIN=8000; EVAL=2000
K_LIST=(4,8,12)
RULES=("UNANIMITY","MAJORITY")
ARMS=("ADAPTIVE_PRIVATE","FIXED_INDEPENDENT_PRIVATE",
      "FIXED_PUBLIC_PRIVATE","RANDOM_CHANNEL_PRIVATE",
      "SIGNAL_FOLLOW_INDEPENDENT","SIGNAL_FOLLOW_PUBLIC","PERFECT_STATE_ORACLE")
ACCURACY=.8; PR_GOOD=.6; CHANNEL_COST=.02; ALPHA=.10
def digest_int(s):
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],"little")
def q_choose(q,eps,rng):
    # Samples exactly uniform random actions when Q ties; eps-greedy elsewhere.
    best=np.argmax(q+1.e-12*rng.random(q.shape),axis=-1)
    explore=rng.random(best.shape)<eps
    return np.where(explore,rng.integers(q.shape[-1],size=best.shape),best).astype(np.int8)
def fixed_loss_worlds(k,worlds=W,groups=G):
    loss=np.empty((worlds,groups,k-1),dtype=np.float64)
    for w in range(worlds):
        rr=np.random.Generator(np.random.Philox(digest_int(f"V194-type-world-v1-{k}-{w}")))
        loss[w]=np.where(rr.random((groups,k-1))<.5,1.,7.)
    return loss
def stage(theta,public,votes,loss,rule):
    m=loss.shape[-1]
    yes_count=np.sum(votes,axis=-1)
    quorum=m if rule=="UNANIMITY" else m//2+1
    accepted=yes_count>=quorum
    raw=np.where(theta[...,None],1.,-loss)
    reward=np.where(accepted[...,None],raw,0.) - CHANNEL_COST*public[...,None]
    return reward,accepted
def scalar_parity():
    rng=np.random.default_rng(194112)
    for _ in range(500):
        k=int(rng.choice(K_LIST));m=k-1
        losses=np.where(rng.random((1,1,m))<.5,1.,7.)
        theta=np.asarray([[bool(rng.integers(0,2))]])
        public=np.asarray([[bool(rng.integers(0,2))]])
        votes=rng.integers(0,2,size=(1,1,m))
        rule="MAJORITY" if rng.random()<.5 else "UNANIMITY"
        got,approved=stage(theta,public,votes,losses,rule)
        n=int(sum(int(v) for v in votes.ravel()))
        quo=m if rule=="UNANIMITY" else m//2+1
        ref=np.array([(1. if theta[0,0] else -float(l))*(n>=quo)-
                      .02*int(public[0,0]) for l in losses.ravel()])
        assert bool(approved[0,0])==(n>=quo)
        assert np.max(np.abs(got.ravel()-ref))<1e-12
        # Transfers only through collective action of this voting institution;
        # group welfare is the mean of individual realizations.
        assert np.isfinite(got).all()
    return 500
def one_arm(k,rule,arm,worlds=W,groups=G,train=TRAIN,eval_steps=EVAL,
            smoke=False):
    t0=time.perf_counter()
    losses=fixed_loss_worlds(k,worlds,groups)
    m=k-1; shape=(worlds,groups,m)
    wi,gi,ai=np.indices(shape)
    q_ch=np.zeros(shape+(2,),dtype=np.float64)
    q_vote=np.zeros(shape+(2,2,2),dtype=np.float64)
    # A genuinely disjoint action RNG; environment streams match across arms.
    rng_act=np.random.Generator(np.random.Philox(digest_int(f"V194-actions-v1-{k}-{rule}-{arm}")))
    env_train=np.random.Generator(np.random.Philox(digest_int(f"V194-env-train-v1-{k}-{rule}")))
    env_test=np.random.Generator(np.random.Philox(digest_int(f"V194-env-holdout-v1-{k}-{rule}")))
    records=[];summary=[]
    for phase,steps,rng_env in (("TRAIN",train,env_train),("EVAL",eval_steps,env_test)):
        accum=dict(world_reward=np.zeros(worlds),world_public=np.zeros(worlds),
                   world_true_positive=np.zeros(worlds),world_false_positive=np.zeros(worlds),
                   world_approve=np.zeros(worlds),world_voteyes=np.zeros(worlds),
                   world_low_loss_reward=np.zeros(worlds),world_high_loss_reward=np.zeros(worlds),
                   world_channel_voteyes=np.zeros(worlds))
        checkpoints=(1000,4000,6000,8000) if phase=="TRAIN" else ()
        for t in range(steps):
            theta=rng_env.random((worlds,groups))<PR_GOOD
            signal_noise=rng_env.random(shape)
            individual_signals=signal_noise < np.where(theta[...,None],ACCURACY,1-ACCURACY)
            if phase=="EVAL":
                eps=0.
            else:
                eps=.3-(.3-.08)*min(t,6000)/6000
            if arm=="ADAPTIVE_PRIVATE":
                channel_vote=q_choose(q_ch,eps,rng_act)
                public=(channel_vote.sum(axis=-1)>m//2)
            elif arm=="RANDOM_CHANNEL_PRIVATE":
                public=rng_act.random((worlds,groups))<.5
                channel_vote=np.broadcast_to(public[...,None],shape)
            elif arm in ("FIXED_PUBLIC_PRIVATE","SIGNAL_FOLLOW_PUBLIC"):
                public=np.ones((worlds,groups),dtype=bool)
                channel_vote=np.ones(shape,dtype=np.int8)
            else:
                public=np.zeros((worlds,groups),dtype=bool)
                channel_vote=np.zeros(shape,dtype=np.int8)
            signal=np.where(public[...,None],individual_signals[:,:,:1],individual_signals)
            if arm=="PERFECT_STATE_ORACLE":
                # Perfect technology, one public decision GOOD iff GOOD,
                # all participants receive the same individual outcome.
                vote=np.broadcast_to(theta[...,None],shape).astype(np.int8)
                public[:]=False
            elif arm.startswith("SIGNAL_FOLLOW"):
                vote=signal.astype(np.int8)
            else:
                channels=np.broadcast_to(public[...,None],shape).astype(np.int8)
                vote_logits=q_vote[wi,gi,ai,channels,signal.astype(np.int8),:]
                vote=q_choose(vote_logits,eps,rng_act)
            reward,accepted=stage(theta,public,vote,losses,rule)
            if phase=="TRAIN":
                if arm=="ADAPTIVE_PRIVATE":
                    old=q_ch[wi,gi,ai,channel_vote]
                    q_ch[wi,gi,ai,channel_vote]=old+ALPHA*(reward-old)
                if arm in ("ADAPTIVE_PRIVATE","FIXED_INDEPENDENT_PRIVATE",
                           "FIXED_PUBLIC_PRIVATE","RANDOM_CHANNEL_PRIVATE"):
                    channels=np.broadcast_to(public[...,None],shape).astype(np.int8)
                    signals=signal.astype(np.int8)
                    old=q_vote[wi,gi,ai,channels,signals,vote]
                    q_vote[wi,gi,ai,channels,signals,vote]=old+ALPHA*(reward-old)
            accum["world_reward"]+=reward.mean(axis=(1,2))/steps
            accum["world_public"]+=public.mean(axis=1)/steps
            accum["world_true_positive"]+=(accepted&theta).mean(axis=1)/steps
            accum["world_false_positive"]+=(accepted&~theta).mean(axis=1)/steps
            accum["world_approve"]+=accepted.mean(axis=1)/steps
            accum["world_voteyes"]+=vote.mean(axis=(1,2))/steps
            accum["world_channel_voteyes"]+=channel_vote.mean(axis=(1,2))/steps
            low=(losses==1);high=~low
            accum["world_low_loss_reward"]+=(reward*low).sum(axis=(1,2))/low.sum(axis=(1,2))/steps
            accum["world_high_loss_reward"]+=(reward*high).sum(axis=(1,2))/high.sum(axis=(1,2))/steps
            if t+1 in checkpoints:
                records.append(dict(phase=phase,at=t+1,
                    reward_so_far=float(np.mean(accum["world_reward"])*steps/(t+1)),
                    public_so_far=float(np.mean(accum["world_public"])*steps/(t+1)),
                    approve_so_far=float(np.mean(accum["world_approve"])*steps/(t+1))))
        record=dict(phase=phase,steps=steps,
            **{k:v.tolist() for k,v in accum.items()},
            **{k+"_mean":float(v.mean()) for k,v in accum.items()})
        summary.append(record)
    # Exact known theory only applies when the strategy follows the signal.
    loss_avg=float(losses.mean())
    quorum=m if rule=="UNANIMITY" else m//2+1
    from math import comb
    def approval_prob(q):
        return sum(comb(m,j)*q**j*(1-q)**(m-j)
                   for j in range(quorum,m+1))
    xg=approval_prob(.8);xb=approval_prob(.2)
    theoretical_signal_follow_indep=.6*xg-.4*loss_avg*xb
    theoretical_signal_follow_public=.6*.8-.4*loss_avg*.2-.02
    return dict(arm=arm,k=k,rule=rule,train=train,eval=eval_steps,
        worlds=worlds,groups=groups,loss_mean=loss_avg,
        losses_world_mean=losses.mean(axis=(1,2)).tolist(),
        training_checkpoints=records,phases=summary,
        q_channel_mean_per_action=q_ch.mean(axis=(0,1,2)).tolist(),
        q_vote_mean_per_ch_sig_act=q_vote.mean(axis=(0,1,2)).tolist(),
        signal_follow_theory_indep=theoretical_signal_follow_indep,
        signal_follow_theory_public=theoretical_signal_follow_public,
        cpu_seconds=time.perf_counter()-t0,
        independent_agent_q=True,training_uses_only_realized_own_reward=True,
        no_group_value_gradient=True,
        channel_preference_learned=arm=="ADAPTIVE_PRIVATE",
        group_membership_learned=False,donation_learned=False,technology_given=True),q_ch,q_vote
def paired_bootstrap(rows,worlds=W):
    rng=np.random.default_rng(digest_int("V194-bootstrap-v1"))
    arms={r["arm"]:r for r in rows}
    out={}
    adaptive=np.asarray(arms["ADAPTIVE_PRIVATE"]["phases"][-1]["world_reward"])
    for rival in ("FIXED_INDEPENDENT_PRIVATE","FIXED_PUBLIC_PRIVATE",
                  "RANDOM_CHANNEL_PRIVATE","SIGNAL_FOLLOW_INDEPENDENT",
                  "SIGNAL_FOLLOW_PUBLIC","PERFECT_STATE_ORACLE"):
        other=np.asarray(arms[rival]["phases"][-1]["world_reward"])
        d=adaptive-other
        idx=rng.integers(0,worlds,size=(10000,worlds))
        av=d[idx].mean(axis=1)
        out["ADAPTIVE_minus_"+rival]=dict(delta=float(d.mean()),
             world_paired_bootstrap95=np.quantile(av,[.025,.975]).tolist(),
             positive_worlds=int((d>0).sum()),negative_worlds=int((d<0).sum()))
    return out
def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--smoke",action="store_true")
    pa.add_argument("--k",type=int,choices=K_LIST)
    pa.add_argument("--rule",choices=RULES)
    pa.add_argument("--worlds",type=int,default=W)
    pa.add_argument("--groups",type=int,default=G)
    pa.add_argument("--train",type=int,default=TRAIN)
    pa.add_argument("--eval",type=int,default=EVAL)
    args=pa.parse_args()
    assert scalar_parity()==500
    print("V194_SCALAR_PARITY_OK 500",flush=True)
    ks=(args.k,) if args.k else (4,) if args.smoke else K_LIST
    rules=(args.rule,) if args.rule else ("UNANIMITY",) if args.smoke else RULES
    count=0
    for k in ks:
        for rule in rules:
            rows=[];qcache={}
            for arm in ARMS:
                r,qch,qv=one_arm(k,rule,arm,
                    worlds=(4 if args.smoke else args.worlds),
                    groups=(5 if args.smoke else args.groups),
                    train=(16 if args.smoke else args.train),
                    eval_steps=(12 if args.smoke else args.eval),
                    smoke=args.smoke)
                rows.append(r)
                if not args.smoke:qcache[arm]=(qch,qv)
                print("V194_ARM",k,rule,arm,"reward",round(r["phases"][-1]["world_reward_mean"],5),
                  "public",round(r["phases"][-1]["world_public_mean"],4),
                  "yes",round(r["phases"][-1]["world_approve_mean"],4),
                  "sec",round(r["cpu_seconds"],1),flush=True)
            if args.smoke:
                continue
            outdir=ROOT/"results"/"V194_PRIVATE_INFORMATION_LEARNING"
            outdir.mkdir(exist_ok=True)
            name=f"V194_k{k}_{rule}_W{args.worlds}_G{args.groups}_T{args.train}.json"
            target=outdir/name
            assert not target.exists(),str(target)
            meta=dict(study="V194 learned information source and votes",date="2026-11-15",
                k=k,rule=rule,n_worlds=args.worlds,n_groups_per_world=args.groups,
                group_membership_exogenous=True,private_loss_types=[1,7],
                world_level_results=True,holdout_new_states_not_new_agent_groups=True,
                training_episodes=args.train,holdout_eval_episodes=args.eval,
                controls=ARMS,independent_world_seed_assignments=True,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                prereg_sha256=hashlib.sha256(
                    (ROOT/"PREREG_V194_PRIVATE_ENDOGENOUS_INFORMATION_VOTE.md").read_bytes()).hexdigest(),
                rows=rows,bootstrap=paired_bootstrap(rows,args.worlds),
                claim_scientific_novelty=False,CT2_historical=61,N2=0,N3=0)
            target.write_text(json.dumps(meta,indent=2),encoding="utf8")
            weights=outdir/name.replace(".json",".npz")
            assert not weights.exists()
            np.savez_compressed(weights,**{f"qch_{a}":qcache[a][0] for a in qcache},
                **{f"qvote_{a}":qcache[a][1] for a in qcache})
            print("V194_COMPLETED",target.name,flush=True)
            count+=1
    if args.smoke:
        print("V194_SMOKE_PASS",flush=True)
    else:
        print("V194_FINISHED",count,flush=True)
if __name__=="__main__":main()
