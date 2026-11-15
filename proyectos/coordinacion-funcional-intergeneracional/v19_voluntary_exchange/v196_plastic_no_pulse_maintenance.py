"""V196: test whether learned private voting conventions survive continued plasticity.
Independent Q per voter, no forced pulses except explicitly-maintained control.
Exact frozen-policy evaluation is computed at all fixed times (not selected peaks).
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PRE=ROOT/"PREREG_V196_PLASTIC_MAINTENANCE_AFTER_EXPLORATION.md"
V195=ROOT/"results/V195_CORRELATED_EXPLORATION"
OUT=ROOT/"results/V196_POST_PULSE_PLASTICITY"
W,G,H=32,20,8000
ARMS=("FREEZE","PLASTIC_NO_PULSE_EPS08","PLASTIC_NO_PULSE_EPS02",
      "PLASTIC_NO_PULSE_EPS00","PLASTIC_KEEP_PULSE_10")
def digest(s):
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],"little")
def world_types(k):
    L=np.empty((W,G,k-1))
    for w in range(W):
        gen=np.random.Generator(np.random.Philox(digest(f"V195-private-stakes-world-{k}-{w}")))
        L[w]=np.where(gen.random((G,k-1))<.5,1.,7.)
    return L
def p_yes(q):
    d=q[...,1]-q[...,0]
    return np.where(d>1e-12,1.,np.where(d< -1e-12,0.,.5))
def tails_batch(ps,h):
    # Poisson-binomial exact dynamic programming on all W*G groups.
    n=ps.shape[-1]
    dp=np.zeros(ps.shape[:2]+(n+1,),dtype=float)
    dp[...,0]=1.
    for i in range(n):
        p=ps[...,i,None]
        old=dp.copy()
        dp[...,0]=old[...,0]*(1-p[...,0])
        dp[...,1:]=old[...,1:]*(1-p)+old[...,:-1]*p
    assert np.max(np.abs(dp.sum(-1)-1))<1e-12
    return dp[...,h:].sum(-1)
def exact_snapshot(q,L,h):
    m=L.shape[-1]
    assert q.shape==(W,G,m,2,2)
    p=p_yes(q)
    pneg,ppos=p[...,0],p[...,1]
    pG=.8*ppos+.2*pneg;pB=.2*ppos+.8*pneg
    agreeG=tails_batch(pG,h);agreeB=tails_batch(pB,h)
    payoff=.6*agreeG-.4*L.mean(-1)*agreeB
    lossperson=.6*agreeG[...,None]-.4*L*agreeB[...,None]
    lo=L==1; hi=~lo
    return dict(
        world_welfare=payoff.mean(axis=1).tolist(),
        world_good_approval=agreeG.mean(1).tolist(),
        world_bad_approval=agreeB.mean(1).tolist(),
        world_null_contract=(agreeG<.01).mean(1).tolist(),
        world_yes_positive=ppos.mean((1,2)).tolist(),
        world_yes_negative=pneg.mean((1,2)).tolist(),
        world_low_stake_payoff=(lossperson*lo).sum((1,2))/lo.sum((1,2)),
        world_high_stake_payoff=(lossperson*hi).sum((1,2))/hi.sum((1,2)),
        mean_welfare=float(payoff.mean()),
        mean_good_approval=float(agreeG.mean()),
        mean_bad_approval=float(agreeB.mean()),
        mean_null_contract=float((agreeG<.01).mean()),
        mean_yes_positive=float(ppos.mean()),
        mean_yes_negative=float(pneg.mean()))
def pick(q,eps,rng):
    best=(q+1e-12*rng.random(q.shape)).argmax(-1)
    roam=rng.random(best.shape)<eps
    return np.where(roam,rng.integers(0,2,size=best.shape),best).astype(np.int8)
def one_case(k,rule,arm,L,original,epochs=H):
    m=k-1;quo=m if rule=="UNANIMITY" else m//2+1
    q=original.copy()
    assert not np.shares_memory(q,original)
    wi,gi,mi=np.indices((W,G,m))
    env=np.random.Generator(np.random.Philox(digest(f"V196-deployment-new-env-{k}-{rule}")))
    rng=np.random.Generator(np.random.Philox(digest(f"V196-private-action-{k}-{rule}-{arm}")))
    init=exact_snapshot(q,L,quo)
    saved=[dict(t=0,phase="initial",**serialize(init))]
    checkpoint=(epochs//4,epochs//2,3*epochs//4,epochs)
    rewards=np.zeros(W);approval=np.zeros(W);pulses=np.zeros(W)
    t0=time.perf_counter()
    for t in range(1,epochs+1):
        good=env.random((W,G))<.6
        signal=env.random((W,G,m))<np.where(good[...,None],.8,.2)
        if arm=="FREEZE" or arm=="PLASTIC_NO_PULSE_EPS00":eps=0.
        elif arm=="PLASTIC_NO_PULSE_EPS02":eps=.02
        else:eps=.08
        votes=pick(q[wi,gi,mi,signal.astype(np.int8),:],eps,rng)
        intervention=np.zeros((W,G),dtype=bool)
        if arm=="PLASTIC_KEEP_PULSE_10":
            intervention=rng.random((W,G))<.10
            votes=np.where(intervention[...,None],signal,votes).astype(np.int8)
        agreed=votes.sum(-1)>=quo
        reward=np.where(agreed[...,None],np.where(good[...,None],1.,-L),0.)
        if arm!="FREEZE":
            old=q[wi,gi,mi,signal.astype(np.int8),votes]
            q[wi,gi,mi,signal.astype(np.int8),votes]=old+.10*(reward-old)
        rewards+=reward.mean((1,2))
        approval+=agreed.mean(axis=1)
        pulses+=intervention.mean(axis=1)
        if t in checkpoint:
            exact=exact_snapshot(q,L,quo)
            saved.append(dict(t=t,phase="adapted",**serialize(exact),
              cumulative_observed_private_reward=float(rewards.mean()/t),
              cumulative_public_pulse=float(pulses.mean()/t),
              cumulative_approval=float(approval.mean()/t)))
            print("V196_CK",k,rule,arm,t,
                  "exact",round(exact["mean_welfare"],5),
                  "initial",round(init["mean_welfare"],5),
                  "null",round(exact["mean_null_contract"],4),
                  "pulse",round(pulses.mean()/t,4),flush=True)
    return dict(arm=arm,checkpoints=saved,
        q_updated=arm!="FREEZE",pulse_used=arm=="PLASTIC_KEEP_PULSE_10",
        total_cumulative_reward=float(rewards.mean()/epochs),
        pulse_rate=float(pulses.mean()/epochs),
        final_q_digest=hashlib.sha256(q.tobytes()).hexdigest(),
        retention_ratio=(saved[-1]["mean_welfare"]/
                         init["mean_welfare"] if abs(init["mean_welfare"])>1e-12 else None),
        time_sec=time.perf_counter()-t0),q
def serialize(snapshot):
    out={}
    for key,val in snapshot.items():
        if isinstance(val,np.ndarray):out[key]=val.tolist()
        else:out[key]=val
    return out
def bootstrap(rows):
    rng=np.random.default_rng(digest("V196-bootstrap-v1"))
    a={x["arm"]:x for x in rows}
    vals={}
    for arm in ARMS:
        i=np.asarray(a[arm]["checkpoints"][0]["world_welfare"])
        end=np.asarray(a[arm]["checkpoints"][-1]["world_welfare"])
        delta=end-i
        idx=rng.integers(0,W,size=(10000,W))
        ci=np.quantile(delta[idx].mean(1),[.025,.975]).tolist()
        vals[arm+"_end_minus_start"]=dict(mean=float(delta.mean()),paired_ci95=ci)
    i=np.asarray(a["PLASTIC_KEEP_PULSE_10"]["checkpoints"][-1]["world_welfare"])
    j=np.asarray(a["PLASTIC_NO_PULSE_EPS08"]["checkpoints"][-1]["world_welfare"])
    d=i-j;idx=rng.integers(0,W,size=(10000,W))
    vals["WITH_PULSE_minus_NO_PULSE_EPS08"]=dict(mean=float(d.mean()),
       paired_ci95=np.quantile(d[idx].mean(1),[.025,.975]).tolist())
    return vals
def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--k",type=int,choices=(4,8,12))
    pa.add_argument("--rule",choices=("UNANIMITY","MAJORITY"))
    pa.add_argument("--smoke",action="store_true")
    pa.add_argument("--episodes",type=int,default=H)
    z=pa.parse_args()
    choices_k=(z.k,) if z.k else ((4,) if z.smoke else (4,8,12))
    choices_rule=(z.rule,) if z.rule else (("UNANIMITY",) if z.smoke else ("UNANIMITY","MAJORITY"))
    for k in choices_k:
        for rule in choices_rule:
            f=V195/f"V195_k{k}_{rule}_W32_G20_T8000.npz"
            original=np.load(f)["JOINT_SIGNAL_PULSE_10"].copy()
            initial_sha=hashlib.sha256(original.tobytes()).hexdigest()
            L=world_types(k);h=k-1 if rule=="UNANIMITY" else k//2
            if not z.smoke:
                audit=V195/f"V195A_FROZEN_NO_PULSE_AUDIT_k{k}_{rule}.json"
                assert audit.exists(),str(audit)
                j=json.loads(audit.read_text("utf8"))
                ref=next(x["exact_welfare"] for x in j["rows"] if x["arm"]=="JOINT_SIGNAL_PULSE_10")
                assert abs(ref-exact_snapshot(original,L,h)["mean_welfare"])<1e-12,(ref,exact_snapshot(original,L,h)["mean_welfare"])
            rows=[];weights={}
            for arm in ARMS:
                dat,q=one_case(k,rule,arm,L,original,
                    epochs=16 if z.smoke else z.episodes)
                if arm=="FREEZE":assert np.array_equal(q,original)
                rows.append(dat);weights[arm]=q
            assert hashlib.sha256(original.tobytes()).hexdigest()==initial_sha
            if z.smoke:
                print("V196_SMOKE_PASS",k,rule,flush=True)
                return
            OUT.mkdir(exist_ok=True)
            f_out=OUT/f"V196_k{k}_{rule}_W32_G20_H{z.episodes}.json"
            assert not f_out.exists()
            o=dict(experiment="V196 plastic maintenance of V195 learned policies",date="2026-11-15",
              group_k=k,rule=rule,group_m=k-1,worlds=W,groups_per_world=G,
              source_v195_sha=hashlib.sha256(f.read_bytes()).hexdigest(),
              source_q_sha=initial_sha,
              method_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              prereg_sha=hashlib.sha256(PRE.read_bytes()).hexdigest(),
              checks_exact_initial_matches_v195a=True,
              tests_per_condition=z.episodes,
              results=rows,comparisons=bootstrap(rows),
              external_adoption_mechanism_learned=False,
              group_membership_exogenous=True,
              code_is_not_scientific_novelty=True,
              AB_CT2=61,N2=0,N3=0)
            f_out.write_text(json.dumps(o,indent=2),encoding="utf8")
            f_weight=OUT/f_out.name.replace(".json",".npz")
            assert not f_weight.exists()
            np.savez_compressed(f_weight,**weights)
            print("V196_DONE",f_out.name,flush=True)
if __name__=="__main__":main()
