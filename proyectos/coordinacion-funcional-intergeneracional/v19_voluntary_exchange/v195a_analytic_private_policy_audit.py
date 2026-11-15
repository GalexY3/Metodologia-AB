"""V195A independent exact calculation of frozen private policies.
Does not simulate games or import the V195 trainer. Cannot certify novelty.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,itertools,json
import numpy as np
ROOT=Path(__file__).resolve().parent
PRE=ROOT/"PREREG_V195A_EXACT_NO_PULSE_VALIDATION.md"
FILES=ROOT/"results"/"V195_CORRELATED_EXPLORATION"
A=.8;PR=.6;WORLD=32;GROUP=20
ARMS=("STANDARD_PRIVATE","IID_SIGNAL_PULSE_10","JOINT_SIGNAL_PULSE_10",
 "JOINT_RANDOM_PULSE_10","JOINT_SIGNAL_PULSE_02",
 "SIGNAL_FOLLOW_CONTROL","ORACLE_STATE")
def population(k):
    L=np.empty((WORLD,GROUP,k-1))
    for w in range(WORLD):
        h=int.from_bytes(hashlib.sha256(f"V195-private-stakes-world-{k}-{w}".encode()).digest()[:8],"little")
        rr=np.random.Generator(np.random.Philox(h))
        L[w]=np.where(rr.random((GROUP,k-1))<.5,1.,7.)
    return L
def choices(q):
    # q shape (..., signal, action): stochastic only for exact ties
    delta=q[...,1]-q[...,0]
    return np.where(delta>1.e-12,1.,np.where(delta<-1.e-12,0.,.5))
def distribution(probs):
    cur=np.array([1.])
    for p in probs:cur=np.convolve(cur,(1-p,float(p)))
    return cur
def tail(probs,threshold):
    return float(distribution(probs)[threshold:].sum())
def brute(probs,threshold):
    ans=0.
    for vote in itertools.product((0,1),repeat=len(probs)):
        if sum(vote)>=threshold:
            p=1.
            for v,s in zip(vote,probs):p*=s if v else 1-s
            ans+=p
    return ans
def scalar_audit():
    rng=np.random.default_rng(195553);maxerr=0
    for i in range(100):
        n=3 if i%2 else 7;h=int(rng.integers(1,n+1))
        p=rng.random(n)
        error=abs(tail(p,h)-brute(p,h))
        maxerr=max(maxerr,error)
        assert error<1.e-12
    return maxerr
def one_group(q,L,h,arm):
    m=len(L)
    if arm=="ORACLE_STATE":
        return dict(welfare=.6,approval_good=1.,approval_bad=0.,
          null_contract=False, mean_vote_regret=None,mean_yes_positive=None,
          mean_yes_negative=None,low_payoff=.6,high_payoff=.6,
          low_yes_positive=None,high_yes_positive=None,
          low_yes_negative=None,high_yes_negative=None)
    if arm=="SIGNAL_FOLLOW_CONTROL":
        yes_pos=np.ones(m);yes_neg=np.zeros(m)
    else:
        yes=choices(q)
        yes_neg,yes_pos=yes[:,0],yes[:,1]
    pG=A*yes_pos+(1-A)*yes_neg
    pB=(1-A)*yes_pos+A*yes_neg
    appG=tail(pG,h);appB=tail(pB,h)
    pv=PR*appG-(1-PR)*L*appB
    regret=[]
    for i in range(m):
        rest=np.delete(np.arange(m),i)
        pivG=distribution(pG[rest])[h-1]
        pivB=distribution(pB[rest])[h-1]
        rs=0
        for s in (0,1):
            pg=A if s else 1-A
            pb=1-A if s else A
            delta=PR*pg*pivG-(1-PR)*L[i]*pb*pivB
            p=float(yes_pos[i] if s else yes_neg[i])
            rs+=max(0.,delta)*(1-p)+max(0.,-delta)*p
        regret.append(rs)
    lo=(L==1.);hi=~lo
    return dict(welfare=float(pv.mean()),
      approval_good=appG,approval_bad=appB,null_contract=appG<.01,
      mean_vote_regret=float(np.mean(regret)),mean_yes_positive=float(yes_pos.mean()),
      mean_yes_negative=float(yes_neg.mean()),low_payoff=float(pv[lo].mean()) if lo.any() else None,
      high_payoff=float(pv[hi].mean()) if hi.any() else None,
      low_yes_positive=float(yes_pos[lo].mean()) if lo.any() else None,
      high_yes_positive=float(yes_pos[hi].mean()) if hi.any() else None,
      low_yes_negative=float(yes_neg[lo].mean()) if lo.any() else None,
      high_yes_negative=float(yes_neg[hi].mean()) if hi.any() else None)
def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--k",type=int,choices=(4,8,12))
    pa.add_argument("--rule",choices=("UNANIMITY","MAJORITY"))
    z=pa.parse_args()
    check=scalar_audit()
    print("V195A_MATH_ENUMERATE 100 error",check,flush=True)
    n=0
    for k in ([z.k] if z.k else (4,8,12)):
        for rule in ([z.rule] if z.rule else ("UNANIMITY","MAJORITY")):
            f=FILES/f"V195_k{k}_{rule}_W32_G20_T8000.json"
            wf=FILES/f"V195_k{k}_{rule}_W32_G20_T8000.npz"
            tgt=FILES/f"V195A_FROZEN_NO_PULSE_AUDIT_k{k}_{rule}.json"
            if not f.exists() or not wf.exists() or tgt.exists():
                print("V195A_SKIP",k,rule,
                    "not_ready" if not f.exists() else "already_audited",flush=True);continue
            raw=json.loads(f.read_text("utf8"));data=np.load(wf)
            L=population(k)
            h=(k-1) if rule=="UNANIMITY" else k//2
            summaries=[]
            for arm in ARMS:
                item=next(x for x in raw["rows"] if x["arm"]==arm)
                assert np.max(np.abs(L.mean((1,2))-np.asarray(item["world_loss_mean"])))<1.e-12
                assert item["phases"][-1]["world_pulse_mean"]==0.,(k,rule,arm,"pulse_leak")
                q=data[arm];assert q.shape==(WORLD,GROUP,k-1,2,2),q.shape
                ws=[]
                for wi in range(WORLD):
                    gg=[one_group(q[wi,gi],L[wi,gi],h,arm) for gi in range(GROUP)]
                    agg={}
                    for name in ("welfare","approval_good","approval_bad","null_contract",
                                  "mean_vote_regret","mean_yes_positive","mean_yes_negative",
                                  "low_payoff","high_payoff","low_yes_positive","high_yes_positive",
                                  "low_yes_negative","high_yes_negative"):
                        vals=[x[name] for x in gg if x[name] is not None]
                        agg[name]=float(np.mean(vals)) if vals else None
                    agg["world"]=wi
                    agg["observed"]=float(item["phases"][-1]["world_reward"][wi])
                    ws.append(agg)
                observed=np.array([x["observed"] for x in ws])
                expected=np.array([x["welfare"] for x in ws])
                d=observed-expected
                rec=dict(arm=arm,
                  exact_welfare=float(expected.mean()),
                  observed_welfare=float(observed.mean()),
                  observed_minus_exact=float(d.mean()),
                  mean_abs_world_monte_carlo_error=float(np.mean(np.abs(d))),
                  max_abs_world_monte_carlo_error=float(np.max(np.abs(d))),
                  monte_carlo_consistent_by_margin=bool(np.mean(np.abs(d))<.03),
                  pulse_train_empirical=float(item["phases"][0]["world_pulse_mean"]),
                  pulse_eval_empirical=float(item["phases"][-1]["world_pulse_mean"]),
                  **{key+"_mean":float(np.mean([x[key] for x in ws if x[key] is not None]))
                    for key in ("approval_good","approval_bad","null_contract",
                                "mean_vote_regret","mean_yes_positive","mean_yes_negative",
                                "low_payoff","high_payoff","low_yes_positive",
                                "high_yes_positive","low_yes_negative","high_yes_negative")
                    if any(x[key] is not None for x in ws)},
                  worlds=ws)
                # Strict check that single-agent and group pulse protocols were
                # not accidentally kept in frozen evaluation.
                if "PULSE_10" in arm:
                    assert abs(rec["pulse_train_empirical"]-.1)<.005,rec
                if "PULSE_02" in arm:
                    assert abs(rec["pulse_train_empirical"]-.02)<.005,rec
                if "PULSE" not in arm:
                    assert rec["pulse_train_empirical"]==0.,arm
                summaries.append(rec)
                print("V195A",k,rule,arm,
                      "EXACT",round(rec["exact_welfare"],6),
                      "OBS",round(rec["observed_welfare"],6),
                      "NULL",round(rec["null_contract_mean"],3),
                      "POSYES",round(rec["mean_yes_positive_mean"],3) if arm!="ORACLE_STATE" else None,
                      "REGRET",round(rec["mean_vote_regret_mean"],4) if arm!="ORACLE_STATE" else None,
                      flush=True)
            res=dict(date="2026-11-15",k=k,rule=rule,w=WORLD,g=GROUP,
              code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              prereg_sha256=hashlib.sha256(PRE.read_bytes()).hexdigest(),
              experiment_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
              weights_sha256=hashlib.sha256(wf.read_bytes()).hexdigest(),
              scalar_enumerations=100,scalar_error_max=check,
              no_intervention_in_evaluation=True,
              independence_limit="analytic evaluator and trainer share same payoff assumptions",
              prior_art="coordinated MARL exploration is known; not original",
              rows=summaries,CT2=61,N2=0,N3=0)
            tgt.write_text(json.dumps(res,indent=2),encoding="utf8")
            print("V195A_DONE",tgt.name,flush=True);n+=1
    print("V195A_COMPLETED",n,flush=True)
if __name__=="__main__":main()
