"""P1 preregistered scale-aware rarity intervention.
No changes after k5..8 holdout lock; one training cohort, 10 test seeds/k.
"""
import hashlib,json,time,statistics
from pathlib import Path
import numpy as np
from model import Society,Parameters,INITIAL_THETA
from model_p1 import ScaleAwareSociety

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results_p1";OUT.mkdir(exist_ok=True)
p=Parameters()
train_seed=20261110
rng=np.random.default_rng(train_seed)
episode_seeds=[int(rng.integers(1,2**31-1)) for _ in range(24)]
k_train=[(2,3,4)[i%3] for i in range(24)]
data=[]
start=time.perf_counter()
trained={}
for mode,cls in (("P0_same_cohort",Society),("P1_k_scaled",ScaleAwareSociety)):
    theta=None
    logs=[]
    for ep,(k,seed) in enumerate(zip(k_train,episode_seeds)):
        s=cls(k,seed,p,theta=theta)
        r=s.run(120,"learned",learning=True)
        theta=s.theta.copy()
        logs.append({"episode":ep,"k":k,"seed":seed,
                     "tv_final":r["final_tv"],"churn_final":r["tail_churn_mean"],
                     "theta_mean":theta.mean(axis=0).tolist()})
    trained[mode]=theta
    np.savez_compressed(OUT/(mode+"_theta.npz"),theta=theta)
    (OUT/(mode+"_train.json")).write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding="utf-8")
    print("P1_TRAIN",mode,"theta",theta.mean(axis=0).round(3).tolist(),
          "elapsed",round(time.perf_counter()-start,1),flush=True)

def evaluate(k:int,seed:int,mode:str)->dict:
    cls=ScaleAwareSociety if mode=="P1_k_scaled" else Society
    if mode=="manual_minority":
        cls=Society
        policy="minority"
        theta=None
    else:
        policy="learned"
        theta=trained[mode]
    sim=cls(k,seed,p,theta=theta)
    w0=sim.theta.copy()
    result=sim.run(140,policy,learning=False)
    assert np.array_equal(w0,sim.theta),"Parameters updated during frozen evaluation"
    return {"mode":mode,"k":k,"seed":seed,
            "final_tv":result["final_tv"],
            "tail_tv":result["tail_tv_mean"],
            "churn":result["tail_churn_mean"],
            "richness":result["tail_local_richness"],
            "stable":result["stable_at_end"],
            "first_stable_tick":result["first_stable_tick"]}
modes=("P0_same_cohort","P1_k_scaled","manual_minority")
known=[]
for k in (2,3,4):
    for s in range(4):
        seed=7000+100*k+s
        for mode in modes:
            known.append(evaluate(k,seed,mode))
summary_known=[{"k":k,"mode":m,
                "stable":sum(z["stable"] for z in known if z["k"]==k and z["mode"]==m),
                "mean_tv":statistics.mean(z["tail_tv"] for z in known if z["k"]==k and z["mode"]==m)}
               for k in (2,3,4) for m in modes]
(OUT/"known_validation.json").write_text(json.dumps({
    "status":"k2..4 only","raw":known,"summary":summary_known},ensure_ascii=False,indent=2),encoding="utf-8")
print("P1_KNOWN",json.dumps(summary_known,ensure_ascii=False),flush=True)

# Lock before accessing k5..8; do not condition on validation outcomes.
lock={
    "protocol":"PROTOCOL_P1_SCALE.md",
    "train_seed":train_seed,"train_k":[2,3,4],
    "eval_k":[5,6,7,8],
    "eval_seed_range":"10000+100*k+s, s=0..9",
    "eval_ticks":140,
    "num_seed_per_k":10,
    "policies":list(modes),
    "model_p0_sha256":hashlib.sha256((ROOT/"model.py").read_bytes()).hexdigest(),
    "model_p1_sha256":hashlib.sha256((ROOT/"model_p1.py").read_bytes()).hexdigest(),
    "trained_weights_hashes":{m:hashlib.sha256((OUT/(m+"_theta.npz")).read_bytes()).hexdigest() for m in trained},
    "params":p.__dict__}
lockfile=OUT/"TEST_LOCK.json"
if lockfile.exists():raise RuntimeError("Test already attempted, do not re-open")
lockfile.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
print("P1_HELDOUT_LOCKED",lock,flush=True)
test=[]
for k in (5,6,7,8):
    for s in range(10):
        seed=10000+100*k+s
        for mode in modes:
            out=evaluate(k,seed,mode)
            test.append(out)
            if mode in ("P0_same_cohort","P1_k_scaled"):
                print("P1_TEST",k,seed,mode,"TV",round(out["tail_tv"],3),
                      "stable",out["stable"],"elapsed",round(time.perf_counter()-start,1),flush=True)
summary=[]
for k in (5,6,7,8):
    for mode in modes:
        r=[z for z in test if z["k"]==k and z["mode"]==mode]
        summary.append({"k":k,"mode":mode,"n":len(r),
            "stable_count":sum(z["stable"] for z in r),
            "mean_tv":statistics.mean(z["tail_tv"] for z in r),
            "mean_churn":statistics.mean(z["churn"] for z in r),
            "mean_richness":statistics.mean(z["richness"] for z in r)})
out={"status":"one-shot heldout k5..8 after P1 training with exactly one feature change",
    "lock":lock,"known":summary_known,
    "test_raw":test,"test_summary":summary,
    "limits":["one training cohort per condition","novel k5..8 are no longer untouched after P1",
              "feature incorporates designed rarity bias; this is not emergent strategy invention"]}
(OUT/"P1_RESULTS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("P1_TEST_SUMMARY",json.dumps(summary,ensure_ascii=False),flush=True)
print("P1_COMPLETE",round(time.perf_counter()-start,1),flush=True)
