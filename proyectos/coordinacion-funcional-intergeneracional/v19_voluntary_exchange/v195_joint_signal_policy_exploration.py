"""V195: endogenous private voting policies after exogenous coordinated exploration.
Policy interventions are imposed ONLY DURING TRAINING, never in deployment.
Actor reward is private realized utility, no shared Q, no centralized critic.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
from math import comb
import numpy as np
ROOT=Path(__file__).resolve().parent
PRE=ROOT/"PREREG_V195_CORRELATED_PRIVATE_EXPLORATION.md"
OUT=ROOT/"results/V195_CORRELATED_EXPLORATION"
W,G,TRAIN,EVAL=32,20,8000,2000
ALPHA=.10;P_GOOD=.6;ACCURACY=.8
ARMS=("STANDARD_PRIVATE","IID_SIGNAL_PULSE_10","JOINT_SIGNAL_PULSE_10",
      "JOINT_RANDOM_PULSE_10","JOINT_SIGNAL_PULSE_02",
      "SIGNAL_FOLLOW_CONTROL","ORACLE_STATE")
K_LIST=(4,8,12);RULES=("UNANIMITY","MAJORITY")
def digest(s):
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],"little")
def world_types(k,w=W,g=G):
    types=np.empty((w,g,k-1),dtype=np.float64)
    for wi in range(w):
        rng=np.random.Generator(np.random.Philox(digest(f"V195-private-stakes-world-{k}-{wi}")))
        types[wi]=np.where(rng.random((g,k-1))<.5,1.,7.)
    return types
def choose(q,epsilon,rng):
    a=(q+1.e-12*rng.random(q.shape)).argmax(axis=-1)
    mask=rng.random(a.shape)<epsilon
    return np.where(mask,rng.integers(0,2,size=a.shape),a).astype(np.int8)
def outcome(true_good,vote,loss,h):
    success=(vote.sum(-1)>=h)
    payoff=np.where(success[...,None],np.where(true_good[...,None],1.,-loss),0.)
    return payoff,success
def parity():
    rng=np.random.default_rng(195889)
    for i in range(500):
        m=int(rng.choice((3,7,11)))
        loss=np.where(rng.random((1,1,m))<.5,1.,7.)
        state=rng.random((1,1))<.6
        vote=rng.integers(0,2,size=(1,1,m))
        h=m if i%2 else m//2+1
        r,acc=outcome(state,vote,loss,h)
        a=int(vote.sum())>=h
        expected=np.array([float(a)*(1. if state[0,0] else -x) for x in loss.ravel()])
        assert a==bool(acc[0,0]) and np.array_equal(expected,r.ravel())
    return 500
def run_arm(k,rule,arm,w=W,g=G,train=TRAIN,test=EVAL):
    m=k-1;h=m if rule=="UNANIMITY" else m//2+1
    loss=world_types(k,w,g)
    shape=(w,g,m)
    wi,gi,mi=np.indices(shape)
    q=np.zeros(shape+(2,2),dtype=float)
    rng_act=np.random.Generator(np.random.Philox(digest(f"V195-actions-{k}-{rule}-{arm}")))
    env_train=np.random.Generator(np.random.Philox(digest(f"V195-env-train-{k}-{rule}")))
    env_test=np.random.Generator(np.random.Philox(digest(f"V195-env-new-eval-{k}-{rule}")))
    t0=time.perf_counter()
    traces=[]
    stats=[]
    for phase,epochs,rng_env in (("TRAIN",train,env_train),("EVAL",test,env_test)):
        agg=dict(world_reward=np.zeros(w),world_true_positive=np.zeros(w),
          world_false_positive=np.zeros(w),world_approved=np.zeros(w),
          world_voteyes=np.zeros(w),world_pulse=np.zeros(w),
          world_low_loss_reward=np.zeros(w),world_high_loss_reward=np.zeros(w),
          world_positive_signal_yes=np.zeros(w),world_negative_signal_yes=np.zeros(w))
        if phase=="TRAIN":checkpoints=(2000,4000,6000,8000)
        else:checkpoints=()
        for t in range(epochs):
            good=rng_env.random((w,g))<P_GOOD
            sig=rng_env.random(shape)<np.where(good[...,None],ACCURACY,1-ACCURACY)
            eps=0. if phase=="EVAL" else .3-(.3-.08)*min(t,6000)/6000
            if arm=="ORACLE_STATE":
                votes=np.broadcast_to(good[...,None],shape).astype(np.int8)
                pulse=np.zeros(shape,dtype=bool)
            elif arm=="SIGNAL_FOLLOW_CONTROL":
                votes=sig.astype(np.int8)
                pulse=np.zeros(shape,dtype=bool)
            else:
                base=choose(q[wi,gi,mi,sig.astype(np.int8),:],eps,rng_act)
                pulse=np.zeros(shape,dtype=bool)
                votes=base
                if phase=="TRAIN":
                    if arm=="IID_SIGNAL_PULSE_10":
                        pulse=rng_act.random(shape)<.1
                        votes=np.where(pulse,sig,base).astype(np.int8)
                    elif arm in ("JOINT_SIGNAL_PULSE_10","JOINT_SIGNAL_PULSE_02"):
                        p=.1 if arm.endswith("10") else .02
                        pulse=np.broadcast_to((rng_act.random((w,g))<p)[...,None],shape)
                        votes=np.where(pulse,sig,base).astype(np.int8)
                    elif arm=="JOINT_RANDOM_PULSE_10":
                        pulse=np.broadcast_to((rng_act.random((w,g))<.1)[...,None],shape)
                        group_random=(rng_act.random((w,g))<.5)
                        votes=np.where(pulse,group_random[...,None],base).astype(np.int8)
            reward,accepted=outcome(good,votes,loss,h)
            if phase=="TRAIN" and arm not in ("ORACLE_STATE","SIGNAL_FOLLOW_CONTROL"):
                old=q[wi,gi,mi,sig.astype(np.int8),votes]
                q[wi,gi,mi,sig.astype(np.int8),votes]=old+ALPHA*(reward-old)
            agg["world_reward"]+=reward.mean(axis=(1,2))/epochs
            agg["world_true_positive"]+=(accepted&good).mean(axis=1)/epochs
            agg["world_false_positive"]+=(accepted&~good).mean(axis=1)/epochs
            agg["world_approved"]+=accepted.mean(axis=1)/epochs
            agg["world_voteyes"]+=votes.mean(axis=(1,2))/epochs
            agg["world_pulse"]+=pulse.mean(axis=(1,2))/epochs
            l=(loss==1.);hl=~l
            agg["world_low_loss_reward"]+=(reward*l).sum((1,2))/l.sum((1,2))/epochs
            agg["world_high_loss_reward"]+=(reward*hl).sum((1,2))/hl.sum((1,2))/epochs
            # Mean yes conditional on positive/negative signal across the world
            agg["world_positive_signal_yes"]+=((votes*sig).sum((1,2))/
                  np.maximum(sig.sum((1,2)),1))/epochs
            agg["world_negative_signal_yes"]+=((votes*(~sig)).sum((1,2))/
                  np.maximum((~sig).sum((1,2)),1))/epochs
            if (t+1) in checkpoints:
                z=epochs/(t+1)
                traces.append(dict(phase=phase,episode=t+1,
                    cumulative_reward=float(np.mean(agg["world_reward"])*z),
                    cumulative_approved=float(np.mean(agg["world_approved"])*z),
                    cumulative_pulse=float(np.mean(agg["world_pulse"])*z),
                    cumulative_yes=float(np.mean(agg["world_voteyes"])*z)))
        stats.append(dict(phase=phase,episodes=epochs,
            **{a:x.tolist() for a,x in agg.items()},
            **{a+"_mean":float(x.mean()) for a,x in agg.items()}))
    return dict(arm=arm,k=k,rule=rule,worlds=w,groups=g,
        world_loss_mean=loss.mean((1,2)).tolist(),
        train_episodes=train,holdout_episodes=test,
        traces=traces,phases=stats,
        q_own_vote_marginal=q.mean((0,1,2)).tolist(),
        elapsed_seconds=time.perf_counter()-t0,
        policy_learning_mode="independent private Q, realized own reward",
        pulse_is_exogenous=True,pulse_in_evaluation=False,
        groups_given=True,roles_given=False,contract_given=True,
        contribution_social_institution_original=False),q
def pair(rows,w):
    rng=np.random.default_rng(digest("V195-bootstrap-32worlds"))
    a={row["arm"]:row for row in rows}
    res={}
    for other in ("IID_SIGNAL_PULSE_10","STANDARD_PRIVATE",
                  "JOINT_RANDOM_PULSE_10","JOINT_SIGNAL_PULSE_02",
                  "SIGNAL_FOLLOW_CONTROL"):
        left=np.asarray(a["JOINT_SIGNAL_PULSE_10"]["phases"][-1]["world_reward"])
        right=np.asarray(a[other]["phases"][-1]["world_reward"])
        delta=left-right
        bs=delta[rng.integers(0,w,size=(10000,w))].mean(1)
        res["JOINT_SIGNAL_10_minus_"+other]=dict(delta=float(delta.mean()),
            world_paired_bootstrap95=np.quantile(bs,[.025,.975]).tolist(),
            n_worlds=w,positive_worlds=int((delta>0).sum()),
            negative_worlds=int((delta<0).sum()))
    return res
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--k",type=int,choices=K_LIST)
    ap.add_argument("--rule",choices=RULES)
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--worlds",type=int,default=W)
    ap.add_argument("--groups",type=int,default=G)
    ap.add_argument("--train",type=int,default=TRAIN)
    ap.add_argument("--eval",type=int,default=EVAL)
    a=ap.parse_args()
    print("V195_PARITY",parity(),flush=True)
    ks=(a.k,) if a.k else (4,) if a.smoke else K_LIST
    rules=(a.rule,) if a.rule else ("UNANIMITY",) if a.smoke else RULES
    for k in ks:
        for rule in rules:
            rows=[];Qs={}
            for arm in ARMS:
                dat,q=run_arm(k,rule,arm,
                    w=4 if a.smoke else a.worlds,g=5 if a.smoke else a.groups,
                    train=30 if a.smoke else a.train,
                    test=30 if a.smoke else a.eval)
                rows.append(dat);Qs[arm]=q
                print("V195_ARM",k,rule,arm,
                    "welfare",round(dat["phases"][-1]["world_reward_mean"],5),
                    "success",round(dat["phases"][-1]["world_true_positive_mean"],4),
                    "yes",round(dat["phases"][-1]["world_voteyes_mean"],4),
                    "pulse",round(dat["phases"][0]["world_pulse_mean"],4),
                    "secs",round(dat["elapsed_seconds"],1),flush=True)
            if a.smoke:continue
            OUT.mkdir(exist_ok=True)
            out=OUT/f"V195_k{k}_{rule}_W{a.worlds}_G{a.groups}_T{a.train}.json"
            assert not out.exists()
            meta=dict(date="2026-11-15",experiment="V195 correlated voluntary-vote policy exploration",
                rule=rule,k=k,w=a.worlds,groups=a.groups,episodes_training=a.train,
                episodes_holdout=a.eval,independent_private_learners=True,
                exogenous_signal_policy_pulses=True,
                pulses_disabled_at_deployment=True,
                agent_roles_not_learnt=True,teams_given=True,contract_rules_given=True,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                prereg_sha256=hashlib.sha256(PRE.read_bytes()).hexdigest(),
                rows=rows,comparisons=pair(rows,a.worlds),
                AB_CT2_unchanged=61,N2=0,N3=0)
            out.write_text(json.dumps(meta,indent=2),encoding="utf8")
            wfile=OUT/out.name.replace(".json",".npz")
            assert not wfile.exists()
            np.savez_compressed(wfile,**{arm:Qs[arm] for arm in ARMS})
            print("V195_COMPLETE",str(out),flush=True)
    if a.smoke:print("V195_SMOKE_PASS",flush=True)
if __name__=="__main__":main()
