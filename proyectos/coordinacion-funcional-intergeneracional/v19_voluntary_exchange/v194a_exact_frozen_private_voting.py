"""V194A post-first-result preregistered exact frozen policy audit.
This computes independent analytic Poisson-binomial policy values (no simulation),
including tie-randomization, private unilateral vote and channel-choice regrets.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,itertools
import numpy as np
ROOT=Path(__file__).resolve().parent
FAMILY=ROOT/"results"/"V194_PRIVATE_INFORMATION_LEARNING"
PREREG=ROOT/"PREREG_V194A_EXACT_FROZEN_STRATEGIC_AUDIT.md"
PI=.6; C=.02; A=.8
LEARNED=("ADAPTIVE_PRIVATE","FIXED_INDEPENDENT_PRIVATE",
         "FIXED_PUBLIC_PRIVATE","RANDOM_CHANNEL_PRIVATE")
ALL_ARMS=LEARNED+("SIGNAL_FOLLOW_INDEPENDENT","SIGNAL_FOLLOW_PUBLIC","PERFECT_STATE_ORACLE")
def p_yes(q):
    delta=q[...,1]-q[...,0]
    return np.where(delta>1.e-12,1.,np.where(delta<-1.e-12,0.,.5))
def pmf(probs):
    ans=np.array([1.],dtype=float)
    for p in probs: ans=np.convolve(ans,[1-float(p),float(p)])
    return ans
def tail(probs,h):
    return float(np.sum(pmf(probs)[h:]))
def exact_enum(probs,h):
    n=len(probs)
    s=0.
    for x in itertools.product((0,1),repeat=n):
        if sum(x)>=h:
            m=1.
            for j,c in enumerate(x):m*=probs[j] if c else 1.-probs[j]
            s+=m
    return s
def arithmetic_audit():
    rng=np.random.default_rng(194111)
    mx=0.
    for i in range(100):
        n=3 if i%2==0 else 7
        p=rng.random(n)
        h=int(rng.integers(1,n+1))
        error=abs(tail(p,h)-exact_enum(p,h))
        mx=max(mx,error)
        assert error<1.e-12,(p,h,error)
    return mx
def world_types(k,W=32,G=20):
    loss=np.empty((W,G,k-1))
    for w in range(W):
        seed=int.from_bytes(hashlib.sha256(f"V194-type-world-v1-{k}-{w}".encode()).digest()[:8],"little")
        rr=np.random.Generator(np.random.Philox(seed))
        loss[w]=np.where(rr.random((G,k-1))<.5,1.,7.)
    return loss
def choose_mode(arm,q_ch,m):
    if arm=="ADAPTIVE_PRIVATE":return p_yes(q_ch)
    if arm in ("FIXED_PUBLIC_PRIVATE","SIGNAL_FOLLOW_PUBLIC"):return np.ones(m)
    if arm=="RANDOM_CHANNEL_PRIVATE":return np.full(m,.5)
    return np.zeros(m)
def channel_approval(arm,qs):
    if arm=="ADAPTIVE_PRIVATE":return tail(qs,len(qs)//2+1)
    if arm=="RANDOM_CHANNEL_PRIVATE":return .5
    return float(qs[0])
def vote_probs(arm,qv):
    if arm in ("SIGNAL_FOLLOW_INDEPENDENT","SIGNAL_FOLLOW_PUBLIC"):
        p=np.zeros((qv.shape[0],2,2))
        p[:,:,1]=1.
        return p
    return p_yes(qv) if arm!="PERFECT_STATE_ORACLE" else np.zeros((qv.shape[0],2,2))
def approval(mode,qp,h):
    pneg=qp[:,mode,0]
    ppos=qp[:,mode,1]
    if mode==0:
        return tail(A*ppos+(1-A)*pneg,h),tail((1-A)*ppos+A*pneg,h)
    a_pos=tail(ppos,h);a_neg=tail(pneg,h)
    return A*a_pos+(1-A)*a_neg,(1-A)*a_pos+A*a_neg
def vote_regret(mode, qp,loss,h):
    m=len(loss)
    r=np.zeros(m)
    if mode==0:
        for i in range(m):
            other=np.delete(np.arange(m),i)
            propG=A*qp[other,0,1]+(1-A)*qp[other,0,0]
            propB=(1-A)*qp[other,0,1]+A*qp[other,0,0]
            pivG=pmf(propG)[h-1];pivB=pmf(propB)[h-1]
            for s in (0,1):
                sg=A if s else 1-A
                sb=1-A if s else A
                delta=PI*sg*pivG-(1-PI)*sb*pivB*loss[i]
                p=qp[i,0,s]
                r[i]+=max(0.,delta)*(1-p)+max(0.,-delta)*p
    else:
        for i in range(m):
            other=np.delete(np.arange(m),i)
            for s in (0,1):
                pivot=pmf(qp[other,1,s])[h-1]
                sg=A if s else 1-A
                sb=1-A if s else A
                delta=pivot*(PI*sg-(1-PI)*sb*loss[i])
                p=qp[i,1,s]
                r[i]+=max(0.,delta)*(1-p)+max(0.,-delta)*p
    return r
def evaluate_one(arm,qch,qvote,loss,h):
    m=len(loss)
    qs=choose_mode(arm,qch,m)
    pub=channel_approval(arm,qs)
    if arm=="PERFECT_STATE_ORACLE":
        return dict(welfare=PI,public=0.,good_approval=1.,bad_approval=0.,
            mean_vote_regret=None,mean_channel_regret=None,exploitability=None,
            null_contract=False,extra_positive_voters=0)
    qp=vote_probs(arm,qvote)
    agr=[];abr=[];eu=[]
    for mode in (0,1):
        a,b=approval(mode,qp,h)
        agr.append(a);abr.append(b)
        eu.append(PI*a-(1-PI)*loss*b-(C if mode else 0.))
    welfare=float(np.mean(pub*eu[1]+(1-pub)*eu[0]))
    vote_r=(1-pub)*vote_regret(0,qp,loss,h)+pub*vote_regret(1,qp,loss,h)
    regret_ch=np.zeros(m)
    if arm=="ADAPTIVE_PRIVATE":
        for i in range(m):
            piv=pmf(np.delete(qs,i))[m//2]
            delta=float(eu[1][i]-eu[0][i])
            regret_ch[i]=piv*(max(0.,delta)*(1-qs[i])+max(0.,-delta)*qs[i])
    # For signal following, strategic regret is defined but not a trained learner.
    approval_g=pub*agr[1]+(1-pub)*agr[0]
    approval_b=pub*abr[1]+(1-pub)*abr[0]
    # Count how many voters would have to change a vote to reach quorum
    # if every individual signal were favorable. Half-ties treated as no.
    active_ind=np.sum(qp[:,0,1]>.5)
    active_pub=np.sum(qp[:,1,1]>.5)
    missing_ind=max(0,h-int(active_ind))
    missing_pub=max(0,h-int(active_pub))
    missing=max(missing_ind,missing_pub) if 0<pub<1 else missing_pub if pub>=1 else missing_ind
    return dict(welfare=welfare,public=float(pub),
       good_approval=float(approval_g),bad_approval=float(approval_b),
       mean_vote_regret=float(np.mean(vote_r)),
       mean_channel_regret=float(np.mean(regret_ch)),
       exploitability=float(np.mean(vote_r+regret_ch)),
       null_contract=approval_g<.01,
       extra_positive_voters=int(missing),
       social_signal_follow_ceiling=float(max(
         PI*agr[0]-(1-PI)*np.mean(loss)*abr[0],
         PI*agr[1]-(1-PI)*np.mean(loss)*abr[1]-C)),
       individual_types=[float(x) for x in loss])
def run_case(k,rule):
    f=FAMILY/f"V194_k{k}_{rule}_W32_G20_T8000.json"
    npz=FAMILY/f"V194_k{k}_{rule}_W32_G20_T8000.npz"
    if not f.exists() or not npz.exists():return None
    audit_existing=FAMILY/f"V194A_exact_strategic_k{k}_{rule}.json"
    if audit_existing.exists():
        print("V194A_PRESERVE_EXISTING",str(audit_existing.name),flush=True)
        return None
    raw=json.loads(f.read_text("utf8"))
    D=np.load(npz)
    W=raw["n_worlds"];G=raw["n_groups_per_world"];m=k-1
    h=m if rule=="UNANIMITY" else m//2+1
    types=world_types(k,W,G)
    per=[]
    for row in raw["rows"]:
        arm=row["arm"]
        qch=D["qch_"+arm]
        qv=D["qvote_"+arm]
        assert qch.shape==(W,G,m,2) and qv.shape==(W,G,m,2,2,2)
        lossmeans=np.asarray(row["losses_world_mean"])
        assert np.max(np.abs(lossmeans-types.mean(axis=(1,2))))<1.e-12
        worlds=[]
        for wi in range(W):
            gs=[evaluate_one(arm,qch[wi,gi],qv[wi,gi],types[wi,gi],h)
                for gi in range(G)]
            obs=row["phases"][-1]["world_reward"][wi]
            worlds.append(dict(world=wi,expected_welfare=float(np.mean([z["welfare"] for z in gs])),
              observed_welfare=float(obs),
              public=float(np.mean([z["public"] for z in gs])),
              approval_good=float(np.mean([z["good_approval"] for z in gs])),
              approval_bad=float(np.mean([z["bad_approval"] for z in gs])),
              null_contract_rate=float(np.mean([z["null_contract"] for z in gs])),
              extra_positive_voters=float(np.mean([z["extra_positive_voters"] for z in gs])),
              mean_vote_regret=(None if gs[0]["mean_vote_regret"] is None else
                    float(np.mean([z["mean_vote_regret"] for z in gs]))),
              mean_channel_regret=(None if gs[0]["mean_channel_regret"] is None else
                    float(np.mean([z["mean_channel_regret"] for z in gs])))))
        val=np.array([z["expected_welfare"] for z in worlds])
        test=np.array([z["observed_welfare"] for z in worlds])
        error=test-val
        rec=dict(arm=arm, exact_predicted_mean=float(val.mean()),
                 actual_holdout_mean=float(test.mean()),
                 mean_residual=float(error.mean()),
                 max_abs_world_residual=float(np.max(np.abs(error))),
                 mean_abs_world_residual=float(np.mean(np.abs(error))),
                 predicted_approval_good=float(np.mean([z["approval_good"] for z in worlds])),
                 predicted_approval_bad=float(np.mean([z["approval_bad"] for z in worlds])),
                 predicted_public=float(np.mean([z["public"] for z in worlds])),
                 low_function_groups=float(np.mean([z["null_contract_rate"] for z in worlds])),
                 additional_positive_voters=float(np.mean([z["extra_positive_voters"] for z in worlds])),
                 vote_regret_per_agent=(None if worlds[0]["mean_vote_regret"] is None else
                     float(np.mean([z["mean_vote_regret"] for z in worlds]))),
                 channel_regret_per_agent=(None if worlds[0]["mean_channel_regret"] is None else
                     float(np.mean([z["mean_channel_regret"] for z in worlds]))),
                 worlds=worlds)
        per.append(rec)
        print("V194A",k,rule,arm,"exact",round(rec["exact_predicted_mean"],5),
              "actual",round(rec["actual_holdout_mean"],5),
              "nullrate",round(rec["low_function_groups"],4),
              "extra_votes",round(rec["additional_positive_voters"],3),
              "regret",None if rec["vote_regret_per_agent"] is None else
                         round(rec["vote_regret_per_agent"],5),flush=True)
    o=FAMILY/f"V194A_exact_strategic_k{k}_{rule}.json"
    assert not o.exists()
    out=dict(k=k,rule=rule,W=W,G=G,training=8000,eval_holdout=2000,
       status="audit of fixed policies not an independent scientific replication",
       case_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
       checkpoint_sha256=hashlib.sha256(npz.read_bytes()).hexdigest(),
       prereg_sha256=hashlib.sha256(PREREG.read_bytes()).hexdigest(),
       code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       exact_scalar_checks=100, exact_scalar_max_error=arithmetic_audit(),
       rows=per,prior_art="Coordination failures in cooperative games and public information known",
       evidence_of_actual_learned_roles_or_institutions=False,N2=0,N3=0)
    o.write_text(json.dumps(out,indent=2),encoding="utf8")
    return o
def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--k",type=int,choices=[4,8,12])
    pa.add_argument("--rule",choices=["UNANIMITY","MAJORITY"])
    a=pa.parse_args()
    print("V194A_PROBABILISTIC_PARITY",arithmetic_audit(),flush=True)
    count=0
    for k in ([a.k] if a.k else [4,8,12]):
        for rule in ([a.rule] if a.rule else ["UNANIMITY","MAJORITY"]):
            x=run_case(k,rule)
            if x:count+=1
    print("V194A_CASES",count,flush=True)
if __name__=="__main__":main()
