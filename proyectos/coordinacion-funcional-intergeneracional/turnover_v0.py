"""G0: matched intergenerational turnover and local cultural-rule transmission.

The minority rule is programmed by the researcher, not spontaneously learned.
Treatment: immediate inherited rule vs no teaching vs probabilistic contact
teaching (p=0.25), SAME demographics and social graph in each arm.
"""
import copy,json,time,statistics,hashlib
from pathlib import Path
import numpy as np
from model import Society,Parameters,minimum_tv_discrete

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results_g0"
OUT.mkdir(exist_ok=True)
P=Parameters()
K=(4,5)
FRACTIONS=(.25,.50,.75)
TREATMENTS=("inherited","no_teaching","contact_teaching")
N_SEEDS=20
BEFORE=140
AFTER=150
TRANSFER_P=.25

def shock(k,seed,fraction):
    shock_rng=np.random.default_rng(np.random.SeedSequence([seed,round(fraction*100),413]))
    n=int(round(fraction*P.n))
    ids=np.sort(shock_rng.choice(P.n,n,replace=False))
    # Fixed exactly across all counterfactuals; deliberately biased new colors.
    new=np.where(shock_rng.random(n)<.70,0,shock_rng.integers(1,k,size=n))
    return ids,new.astype(np.int32)

def prepare(pre:Society,idx:np.ndarray,new:np.ndarray):
    state=copy.deepcopy(pre)
    state.colors[idx]=new
    state.memory[idx,:]=1/pre.k
    state.t=0
    state.history=[]
    state.record(0,0)
    return state

def run_treatment(pre:Society,idx:np.ndarray,new:np.ndarray,
                  treatment:str,teach_seed:int)->dict:
    s=prepare(pre,idx,new)
    known=np.ones(P.n,dtype=bool)
    if treatment!="inherited":known[idx]=False
    teacher=np.random.default_rng(teach_seed)
    initial_tv=s.global_tv()
    initial_colors=s.colors.copy()
    known_series=[float(known.mean())]
    transmissions=0
    contacted=0
    for _ in range(AFTER):
        pairs=s.matching()
        old=s.colors.copy()
        next_colors=old.copy()
        for i,j in pairs:
            ci=int(old[i]);cj=int(old[j])
            s.memory[i]*=P.memory_decay
            s.memory[j]*=P.memory_decay
            s.memory[i,cj]+=1
            s.memory[j,ci]+=1
        learn=[]
        for i,j in pairs:
            next_colors[i]=s._choose(i,int(old[j]),"minority" if known[i] else "stay",learning=False)
            next_colors[j]=s._choose(j,int(old[i]),"minority" if known[j] else "stay",learning=False)
            if treatment=="contact_teaching":
                if known[i] and not known[j] and teacher.random()<TRANSFER_P:
                    learn.append(j)
                if known[j] and not known[i] and teacher.random()<TRANSFER_P:
                    learn.append(i)
        s.colors=next_colors
        s.t+=1
        contacted+=len(pairs)*2
        s.record(float(np.mean(old!=next_colors)),len(pairs)*2)
        # Transmission only affects the NEXT tick's policy.
        for node in learn:
            if not known[node]:
                known[node]=True
                transmissions+=1
        known_series.append(float(known.mean()))
    assert all(0<=c<s.k for c in s.colors)
    window=P.stability_window
    events=[]
    for end in range(window,len(s.history)):
        recent=s.history[end-window+1:end+1]
        if all(v["tv"]<=P.stability_tv and v["churn"]<=P.stability_churn for v in recent):
            events.append(end)
    t_recover=events[0] if events else None
    tv=[v["tv"] for v in s.history]
    auc=float(sum((tv[i]+tv[i+1])/2 for i in range(AFTER)))
    return {"treatment":treatment,"initial_tv":initial_tv,
        "initial_colors_sha256":hashlib.sha256(initial_colors.tobytes()).hexdigest(),
        "replacement_nodes_sha256":hashlib.sha256(idx.tobytes()).hexdigest(),
        "replacement_n":len(idx),
        "recovered_by_150":t_recover is not None,
        "recovery_confirmed_endtick":t_recover,
        "auc_tv_150":auc,
        "final_tv":tv[-1],
        "tail_tv":float(np.mean(tv[-window:])),
        "tail_churn":float(np.mean([v["churn"] for v in s.history[-window:]])),
        "tail_richness":float(np.mean([v["richness"] for v in s.history[-window:]])),
        "frac_rule_before":known_series[0],
        "frac_rule_after":known_series[-1],
        "transmission_count":transmissions,
        "total_participations":contacted,
        "final_colors_sha256":hashlib.sha256(s.colors.tobytes()).hexdigest()}

def main():
    if (OUT/"G0_RESULTS.json").exists():raise RuntimeError("Already completed; never overwrite original")
    results=[];eligible=0;ineligible=[]
    start=time.perf_counter()
    for k in K:
        for serial in range(N_SEEDS):
            seed=12000+k*100+serial
            pre=Society(k,seed,P)
            outcome=pre.run(BEFORE,"minority",learning=False)
            if not outcome["stable_at_end"]:
                ineligible.append({"k":k,"seed":seed,"prior_tv":outcome["tail_tv_mean"],
                                   "prior_churn":outcome["tail_churn_mean"]})
                print("G0_INELIGIBLE",k,seed,outcome["tail_tv_mean"],flush=True)
                continue
            eligible+=1
            for fraction in FRACTIONS:
                idx,colors=shock(k,seed,fraction)
                same=[]
                for treatment in TREATMENTS:
                    v=run_treatment(pre,idx,colors,treatment,
                                    teach_seed=seed*1000+round(fraction*100))
                    v.update({"k":k,"seed":seed,"fraction_replaced":fraction,
                              "pre_tv":outcome["tail_tv_mean"],"pre_churn":outcome["tail_churn_mean"],
                              "min_discrete_tv":minimum_tv_discrete(P.n,k)})
                    same.append(v);results.append(v)
                for key in ("initial_colors_sha256","replacement_nodes_sha256","initial_tv"):
                    if len(set(z[key] for z in same))!=1:
                        raise RuntimeError(f"counterfactual pairing broken: {k}/{seed}/{fraction}/{key}")
                print("G0",k,seed,fraction,
                    "initialTV",round(same[0]["initial_tv"],3),
                    "recover",[(z["treatment"],z["recovery_confirmed_endtick"]) for z in same],
                    "teaching",same[2]["transmission_count"],
                    "elapsed",round(time.perf_counter()-start,1),flush=True)
    groups=[]
    for k in K:
        for fraction in FRACTIONS:
            for treatment in TREATMENTS:
                z=[v for v in results if v["k"]==k and v["fraction_replaced"]==fraction
                   and v["treatment"]==treatment]
                if not z:continue
                groups.append({"k":k,"fraction":fraction,"treatment":treatment,"n_eligible_pre":len(z),
                    "recovered":sum(u["recovered_by_150"] for u in z),
                    "mean_initial_tv":statistics.mean(u["initial_tv"] for u in z),
                    "mean_auc_tv":statistics.mean(u["auc_tv_150"] for u in z),
                    "mean_final_tv":statistics.mean(u["final_tv"] for u in z),
                    "mean_knowledge_final":statistics.mean(u["frac_rule_after"] for u in z),
                    "mean_transmissions":statistics.mean(u["transmission_count"] for u in z),
                    "mean_recovery_time_given_observed":statistics.mean(u["recovery_confirmed_endtick"]
                        for u in z if u["recovered_by_150"]) if any(u["recovered_by_150"] for u in z) else None})
    data={"protocol":"PROTOCOL_TURNOVER_V0.md",
        "status":"exploratory simulation, researcher-programmed minority rule",
        "parameters":{"n":P.n,"k":K,"replacements":FRACTIONS,
                      "transmission_probability":TRANSFER_P,
                      "pre_ticks":BEFORE,"post_ticks":AFTER,
                      "initial_bias_majority":P.init_majority,
                      "recovery":"10 consecutive ticks TV<=.06 churn<=.05"},
        "n_base_attempted":len(K)*N_SEEDS,
        "n_base_eligible":eligible,"ineligible":ineligible,
        "raw":results,"groups":groups}
    (OUT/"G0_RESULTS.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print("G0_COMPLETE",len(results),"branches",eligible,"base cohorts",
          len(ineligible),"base excluded","time",round(time.perf_counter()-start,1),flush=True)
    print("G0_GROUPS",json.dumps(groups,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
