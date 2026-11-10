"""Sealed holdout: first and only final evaluation after target completed.

Never select the 'best' checkpoint. Test-world seeds and metrics were fixed
before V6 training, reported per k and arm, with 100 worlds nested per one
network training. Exact quotas are checked by counts, not D-only thresholds.
"""
from pathlib import Path
from dataclasses import asdict
import torch,sys,json,hashlib,time
from engine import Society,IndependentPolicy,Settings
from trainer import atomic_json
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
RUN=ROOT/"runs"/"principal"
OUT=RUN/"holdout"
ARMS=("trained_sample","trained_greedy","trained_no_messages",
      "untrained_sample","random_always","random_stop24")
SEED=847202611
N_WORLDS=100
STEPS=96
def hash_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as file:
        for chunk in iter(lambda:file.read(2**20),b""):h.update(chunk)
    return h.hexdigest()

@torch.no_grad()
def check(model,cfg,k,arm):
    c=Settings(**{**asdict(cfg),"batch":N_WORLDS,"horizon":STEPS})
    torch.manual_seed(SEED+k*100)
    if c.device=="cuda":torch.cuda.manual_seed_all(SEED+k*100)
    w=Society(c,torch.full((N_WORLDS,),k,device=c.device,dtype=torch.long))
    hist_D=[w.D.clone()]
    hist_churn=[]
    exacts=[]
    for t in range(STEPS):
        if arm=="random_stop24" and t>=24:
            nextcolor=w.colors.clone()
            slot=torch.full_like(nextcolor,5);request=nextcolor.clone()
            requests=torch.zeros(N_WORLDS,w.n,10,device=c.device)
        elif arm.startswith("random"):
            nextcolor=torch.randint(0,10,(N_WORLDS,w.n),device=c.device)
            slot=torch.full_like(nextcolor,5);request=nextcolor.clone()
            requests=torch.zeros(N_WORLDS,w.n,10,device=c.device)
        else:
            a=model.decisions(w,greedy=arm=="trained_greedy",
                 disable_messages=(arm=="trained_no_messages"))
            nextcolor,slot,request,requests=a["choice"],a["slot"],a["request"],a["rec"]
        _,churn=w.advance(nextcolor,slot,request,requests)
        hist_D.append(w.D.clone());hist_churn.append(churn)
        exacts.append(w.exact())
    D=torch.stack(hist_D)
    R=torch.stack(hist_churn)
    E=torch.stack(exacts)
    stable=((D[-10:]<=.02)&(R[-10:]<=.05)).all(0)
    stable_exact=E[-10:].all(0)&(R[-10:]<=.05).all(0)
    return {"arm":arm,"k":k,"n_worlds":N_WORLDS,"turns":STEPS,
            "initial_D":float(D[0].mean()),
            "final_D":float(D[-1].mean()),"mean_D":float(D[1:].mean()),
            "mean_occupied":float((w.counts()>0).sum(-1).float().mean()),
            "exact_final":int(E[-1].sum()),"ever_exact":int(E.any(0).sum()),
            "stable":int(stable.sum()),"exact_and_stable":int(stable_exact.sum()),
            "churn_tail10":float(R[-10:].mean()),
            "curve":D.mean(-1).cpu().tolist(),
            "final_D_worlds":D[-1].cpu().tolist()}
def main():
    st=json.loads((RUN/"status.json").read_text(encoding="utf-8"))
    if st["state"]!="completed":raise RuntimeError("Final target must complete first")
    cp=RUN/"latest.pt"
    conf=json.loads((RUN/"config.json").read_text(encoding="utf-8"))
    cfg=Settings(**{k:conf[k] for k in asdict(Settings()).keys()})
    if cfg.device=="cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA needed for original model; please run on desktop")
    checkpoint=torch.load(cp,map_location=cfg.device,weights_only=False)
    if checkpoint["updates"]*cfg.batch<st["target_episodes"]:
        raise RuntimeError("Model is an intermediate checkpoint")
    lock={"protocol":"PREREG_V6.md","checkpoint_sha256":hash_file(cp),
      "engine_sha256":hash_file(ROOT/"engine.py"),"trainer_sha256":hash_file(ROOT/"trainer.py"),
      "validation_sha256":hash_file(ROOT/"validate.py"),"seed":SEED,
      "worlds_per_arm_k":N_WORLDS,"turns":STEPS,"k":[2,3,4],"arms":list(ARMS),
      "one_training_seed":cfg.seed,"no_checkpoint_selection":True}
    OUT.mkdir(exist_ok=True)
    lf=OUT/"LOCK.json"
    if lf.exists():
        if json.loads(lf.read_text(encoding="utf-8"))!=lock:raise RuntimeError("Holdout lock mismatch")
    else:atomic_json(lf,lock)
    if (OUT/"SUMMARY.json").exists():raise RuntimeError("Already evaluated final test.")
    model=IndependentPolicy(cfg.side**2,cfg.hidden).to(cfg.device)
    model.load_state_dict(checkpoint["model"])
    model.eval()
    torch.manual_seed(cfg.seed)
    untrained=IndependentPolicy(cfg.side**2,cfg.hidden).to(cfg.device)
    untrained.eval()
    rows=[]
    t0=time.perf_counter()
    for k in (2,3,4):
        for arm in ARMS:
            path=OUT/f"k{k}_{arm}.json"
            if path.exists():
                row=json.loads(path.read_text(encoding="utf-8"))
            else:
                policy=untrained if arm.startswith("untrained") else model
                row=check(policy,cfg,k,arm)
                atomic_json(path,row)
            rows.append({key:value for key,value in row.items()
               if key not in ("curve","final_D_worlds")})
            print("FINAL_TEST",k,arm,"D",round(row["final_D"],5),
                  "exact",row["exact_final"],"stable",row["stable"],
                  "elapsed",round(time.perf_counter()-t0,1),flush=True)
    atomic_json(OUT/"SUMMARY.json",{"lock":lock,"metrics":rows,
       "interpretation":"100 held-out worlds per arm are not independent policy-training replications",
       "all_arms_complete":True})
    print("SEALED_EVALUATION_COMPLETE",flush=True)
if __name__=="__main__":main()
