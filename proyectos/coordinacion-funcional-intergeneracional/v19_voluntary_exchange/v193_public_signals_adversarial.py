"""V193: prospective adversarial falsifier for V167 public correlation.
No endogenous learning; conditional voting follows exogenous binary signals.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction
from math import comb
import json,hashlib,time
import numpy as np
BASE=Path(__file__).resolve().parent
OUT=BASE/"results/V193_INFORMATION_RISK_FALSIFIER.json"
PREG=BASE/"PREREG_V193_INFORMATION_RISK_FALSIFIER.md"
W=64;EPISODES=3000;K_LIST=[4,8,12,24];LOSS_LIST=[1,3,5,8]
PI=Fraction(3,5);ACC=Fraction(4,5);COST=Fraction(1,50); BENEFIT=Fraction(1,1)
MODES=("INDEPENDENT","PUBLIC")
RULES=("UNANIMITY","MAJORITY")

def binomial_tail(m,h,p):
    return sum((Fraction(comb(m,j))*p**j*(1-p)**(m-j) for j in range(h,m+1)),Fraction())

def exact(k,mode,rule,L):
    m=k-1
    h=m if rule=="UNANIMITY" else m//2+1
    if mode=="PUBLIC":
        ag,ab=ACC,1-ACC
    else:
        ag=binomial_tail(m,h,ACC);ab=binomial_tail(m,h,1-ACC)
    welfare=PI*ag*BENEFIT-(1-PI)*ab*L-(COST if mode=="PUBLIC" else 0)
    return dict(good_approval=float(ag),bad_approval=float(ab),
                overall_good_approval=float(PI*ag),
                overall_bad_approval=float((1-PI)*ab),
                welfare=float(welfare),
                exact_welfare_fraction=str(welfare.numerator)+"/"+str(welfare.denominator),
                threshold=h)

def arr_record(good,appr,L,public):
    good_n=good.sum(1)
    bad_n=(~good).sum(1)
    assert np.all(good_n>0) and np.all(bad_n>0)
    true=(appr &good).sum(1)/good_n
    false=(appr &~good).sum(1)/bad_n
    expected=(np.where(good,1.,-float(L))*appr).mean(1)-(.02 if public else 0.)
    return dict(world_true_positive=true,world_false_positive=false,
        world_approval_good=(appr&good).mean(1),
        world_approval_bad=(appr&~good).mean(1),
        world_welfare=expected,
        approval=np.mean(appr,axis=1))

def bootstrap_delta(d,rng):
    ids=rng.integers(0,W,size=(10000,W))
    means=d[ids].mean(1)
    return np.quantile(means,[.025,.975]).tolist()

def main():
    assert not OUT.exists()
    t0=time.perf_counter()
    saved=[]
    rng_bs=np.random.default_rng(193000201)
    experiments={}
    for k in K_LIST:
        m=k-1
        rng=np.random.default_rng(1930000+int.from_bytes(
                hashlib.sha256(f"V193-physical-k-{k}".encode()).digest()[:4],"little"))
        good=rng.random((W,EPISODES))<float(PI)
        uniform=rng.random((W,EPISODES,m))
        positive=uniform < np.where(good[...,None],float(ACC),float(1-ACC))
        public=positive[:,:,0]
        for rule in RULES:
            threshold=m if rule=="UNANIMITY" else m//2+1
            approved={"INDEPENDENT":positive.sum(-1)>=threshold,
                      "PUBLIC":public}
            # Data and independent rational theory computed before L loop
            for L in LOSS_LIST:
                arms={}
                for mode in MODES:
                    theory=exact(k,mode,rule,L)
                    sims=arr_record(good,approved[mode],L,mode=="PUBLIC")
                    aggregate={key:float(np.mean(v)) for key,v in sims.items()}
                    arms[mode]=dict(theory=theory,sim=aggregate,
                        deviation={key:float(aggregate[key]-theory[target]) 
                                  for key,target in (
                                    ("world_true_positive","good_approval"),
                                    ("world_false_positive","bad_approval"),
                                    ("world_welfare","welfare"))},
                        world_welfare=sims["world_welfare"].tolist(),
                        world_true_positive=sims["world_true_positive"].tolist(),
                        world_false_positive=sims["world_false_positive"].tolist())
                diff=np.array(arms["PUBLIC"]["world_welfare"])-np.array(arms["INDEPENDENT"]["world_welfare"])
                predicted=arms["PUBLIC"]["theory"]["welfare"]-arms["INDEPENDENT"]["theory"]["welfare"]
                ci=bootstrap_delta(diff,rng_bs)
                cell=dict(k=k,m=m,rule=rule,L=L,arms=arms,
                    predicted_public_minus_independent=predicted,
                    observed_public_minus_independent=float(diff.mean()),
                    bootstrap95=ci, predicted_within_bootstrap95=ci[0]<=predicted<=ci[1],
                    positive_worlds=int((diff>0).sum()),negative_worlds=int((diff<0).sum()),
                    design_pairing="same theta and first private uniform public source")
                saved.append(cell)
                if rule=="UNANIMITY":
                    print("V193",k,rule,L,"public-minus-independent",round(diff.mean(),5),
                        "theory",round(predicted,5),"CI",np.round(ci,5),flush=True)
        experiments[str(k)]=dict(n_per_world=EPISODES,
                good_world_average=float(good.mean()),
                bad_world_average=float((~good).mean()))
    key={(r["k"],r["rule"],r["L"]):r for r in saved}
    gates={
     "unanimity_k4_L3_public_loses":key[(4,"UNANIMITY",3)]["predicted_public_minus_independent"]<0,
     "unanimity_k8_L3_public_wins":key[(8,"UNANIMITY",3)]["predicted_public_minus_independent"]>0,
     "unanimity_k8_L5_public_loses":key[(8,"UNANIMITY",5)]["predicted_public_minus_independent"]<0,
     "unanimity_k24_L5_public_wins":key[(24,"UNANIMITY",5)]["predicted_public_minus_independent"]>0,
     "majority_k24_L1_independent_wins":key[(24,"MAJORITY",1)]["predicted_public_minus_independent"]<0,
    }
    assert all(gates.values()),gates
    theory_ci_misses=[dict(k=z["k"],rule=z["rule"],L=z["L"],
                          predicted=z["predicted_public_minus_independent"],ci=z["bootstrap95"])
                    for z in saved if not z["predicted_within_bootstrap95"]]
    obj=dict(experiment="V193 information risk adversarial test",date="2026-11-15",
        classification="analytic simulation and rule-following signals, NO learned institution",
        claim_original_theorem=False,k=K_LIST,losses=LOSS_LIST,worlds=W,episodes_per_world=EPISODES,
        signal_accuracy=float(ACC),good_prior=float(PI),public_information_cost=float(COST),
        preregistration_sha256=hashlib.sha256(PREG.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        preregistered_qualitative_predictions=gates,ci_coverage_misses=theory_ci_misses,
        encounters_per_k=W*EPISODES,
        worlds_summary=experiments,rows=saved,elapsed=time.perf_counter()-t0,
        CT2_unchanged=61,N2=0,N3=0)
    OUT.write_text(json.dumps(obj,indent=2),encoding="utf-8")
    print("V193_COMPLETE",json.dumps(dict(rows=len(saved),gates=gates,
           theory_ci_misses=len(theory_ci_misses),elapsed=obj["elapsed"])),flush=True)
if __name__=="__main__":main()
