"""V2-C: sealed replication at seeds222/223, independent learned populations.

Test seeds distinct from training and prior V2-B holdout. No gradients.
"""
from pathlib import Path
import hashlib,json,time,statistics
import torch
from environment import VectorSociety,Configuration
from agents import LocalActor

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"replication"
OUT.mkdir(exist_ok=True)
torch.set_num_threads(2)
TRAIN_SEEDS=(222,223)
MODES=(0.,2.)
def filehash(path):return hashlib.sha256(path.read_bytes()).hexdigest()
CHECKPOINTS={(seed,weight):ROOT/"runs"/f"credit{weight:g}_seed{seed}_u180"/"checkpoint_0180.pt"
    for seed in TRAIN_SEEDS for weight in MODES}
LOCK={
 "protocol":"PREREG_REPLICATION.md",
 "actor_sha":filehash(ROOT/"agents.py"),
 "env_sha":filehash(ROOT/"environment.py"),
 "source_sha":filehash(ROOT/"test_replication.py"),
 "checkpoint_sha":{f"{s}_{w:g}":filehash(p) for (s,w),p in CHECKPOINTS.items()},
 "new_training_seed_cohorts":list(TRAIN_SEEDS),
 "weights":list(MODES),"ks":[2,3,4],
 "grid_shapes":[[6,6],[10,12]],
 "eval_batch_by_N":{36:64,120:40},
 "n_iterations":90,
 "world_seed":"970000 or 980000 +1000*training_seed+100*k",
 "stability":"D<=.06 and churn<=.05 for last 10 rounds",
 "parameters_frozen":True
}
path_lock=OUT/"TEST_LOCK.json"
if path_lock.exists():
 before=json.loads(path_lock.read_text(encoding="utf-8"))
 if before!=LOCK:raise RuntimeError("Locked evidence changed; cannot rerun")
else:
 path_lock.write_text(json.dumps(LOCK,indent=2,ensure_ascii=False),encoding="utf-8")
print("REPLICATION_LOCKED",len(CHECKPOINTS),"checkpoints",flush=True)
actors={}
for (seed,weight),path in CHECKPOINTS.items():
 state=torch.load(path,map_location="cpu",weights_only=False)
 p=LocalActor(hidden=state["config"]["hidden"])
 p.load_state_dict(state["actor"])
 p.eval()
 actors[(seed,weight)]=p

@torch.no_grad()
def eval_case(actor,seed_world,k,rows,cols,batch,mode):
    env=VectorSociety(Configuration(rows=rows,cols=cols,batch=batch,
                                    seed=seed_world,randomize_majority=True))
    env.reset(k=k)
    torch.manual_seed(seed_world+len(mode)*61)
    v=[env.tv().clone()]
    c=[]
    sends=[]
    accepts=[]
    for t in range(90):
        obs=env.observe()
        if mode=="stay":
            a=torch.zeros(batch,env.n,dtype=torch.long)
            inc,req,snap=env.deliveries(obs,a)
            q=torch.zeros_like(a)
        else:
            send,_,_,h=actor.sample_sender(obs,env.send_mask(),
                                            random_baseline=(mode=="random"))
            inc,req,snap=env.deliveries(obs,send)
            q,_,_=actor.sample_receiver(h,snap,inc,req,
                                       random_baseline=(mode=="random"))
            a=send
        result=env.step(a,q,inc,req)
        v.append(result["tv"].clone())
        c.append(result["churn"].clone())
        sends.append(result["messages"].clone())
        accepts.append(result["acceptances"].clone())
    tv=torch.stack(v)
    churn=torch.stack(c)
    stable=((tv[-10:]<=.06)&(churn[-10:]<=.05)).all(0)
    return {"initial_mean_TV":float(tv[0].mean()),
      "mean_last10_TV":float(tv[-10:].mean()),
      "mean_final_TV":float(tv[-1].mean()),
      "mean_last10_churn":float(churn[-10:].mean()),
      "stable_count":int(stable.sum()),
      "stable_fraction":float(stable.float().mean()),
      "exact_final_count":int((tv[-1].abs()<1e-6).sum()),
      "ever_below_006_count":int((tv<=.06).any(0).sum()),
      "mean_sends":float(torch.stack(sends).mean()),
      "mean_accepts":float(torch.stack(accepts).mean()),
      "per_world_stable":stable.tolist(),
      "per_world_final_tv":tv[-1].tolist(),
      "mean_tv_curve":[float(z) for z in tv.mean(1)]}

def main():
    t0=time.perf_counter()
    results=[]
    for seed in TRAIN_SEEDS:
        for rows,cols in ((6,6),(10,12)):
            n=rows*cols
            batch=64 if n==36 else 40
            for k in (2,3,4):
                worldseed=(970000 if n==36 else 980000)+1000*seed+100*k
                conditions=[
                    ("credit0",actors[(seed,0.)],"learned"),
                    ("credit2",actors[(seed,2.)],"learned"),
                    ("random",actors[(seed,2.)],"random"),
                    ("stay",actors[(seed,2.)],"stay")]
                for label,policy,mode in conditions:
                    path=OUT/f"N{n}_train{seed}_k{k}_{label}.json"
                    if path.exists():raise RuntimeError("Reevaluating fixed test not allowed: "+str(path))
                    row={"n":n,"train_seed":seed,"world_seed":worldseed,
                         "k":k,"label":label,"world_count":batch,
                         **eval_case(policy,worldseed,k,rows,cols,batch,mode)}
                    path.write_text(json.dumps(row,indent=2,ensure_ascii=False),encoding="utf-8")
                    results.append({k:v for k,v in row.items() if k not in
                        ("per_world_stable","per_world_final_tv","mean_tv_curve")})
                    print("V2C",n,seed,k,label,
                          "D",round(row["mean_last10_TV"],4),
                          "stable",row["stable_count"],"/",batch,
                          "exact",row["exact_final_count"],"/",batch,
                          "elapsed",round(time.perf_counter()-t0,1),flush=True)
    out=OUT/"REPLICATION_SUMMARY.json"
    if out.exists():raise RuntimeError("Output exists")
    out.write_text(json.dumps({"lock":LOCK,"cases":results,
       "n_independent_new_training_cohorts":2,
       "cautions":["seed221 earlier model is a third, previously inspected training cohort",
                   "test episodes are nested under each trained model",
                   "central difference rewards are trainer-only, not decentralized reward discovery",
                   "N120 is size transfer only, k labels same as training"]},
       indent=2,ensure_ascii=False),encoding="utf-8")
    print("V2C_FINISHED",len(results),"cases",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
