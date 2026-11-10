"""Locked heldout evaluation of V2-A2C global vs V2-B difference reward.

Agents use only local observations, direct messages, and previous public
team feedback. No parameter updates; no evaluation data is used for tuning.
"""
from pathlib import Path
import hashlib,json,statistics,time
import numpy as np
import torch
from environment import VectorSociety,Configuration
from agents import LocalActor

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"holdout"
OUT.mkdir(exist_ok=True)
torch.set_num_threads(2)

CKS={
 "team_only":ROOT/"runs"/"credit0_seed221_u180"/"checkpoint_0180.pt",
 "credit_difference":ROOT/"runs"/"credit2_seed221_u180"/"checkpoint_0180.pt"}
def hashfile(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
SPEC={"protocol":"PREREG_HOLDOUT.md",
 "checkpoints_sha256":{k:hashfile(v) for k,v in CKS.items()},
 "environment_sha256":hashfile(ROOT/"environment.py"),
 "actor_sha256":hashfile(ROOT/"agents.py"),
 "evaluator_sha256":hashfile(ROOT/"evaluate_sealed.py"),
 "N36":{"rows":6,"cols":6,"batch":96,"steps":90,"k":[2,3,4],
        "world_seed":"940000+100*k",
        "conditions":["difference_stochastic","team_stochastic","difference_deterministic",
                      "random","stay","one_sender","strip_snapshot","no_previous_feedback"]},
 "N120":{"rows":10,"cols":12,"batch":60,"steps":90,"k":[2,3,4],
         "world_seed":"950000+100*k",
         "conditions":["difference_stochastic","team_stochastic","random","stay"]},
 "global_feedback_at_evaluation":True,
 "training_updates":0,
 "stability":"TV<=.06 and churn<=.05 for final ten rounds"}
LOCK=OUT/"TEST_LOCK.json"
if LOCK.exists():
 prev=json.loads(LOCK.read_text(encoding="utf-8"))
 if prev!=SPEC:raise RuntimeError("Evaluation code/weights differ from frozen lock")
else:
 LOCK.write_text(json.dumps(SPEC,indent=2,ensure_ascii=False),encoding="utf-8")
print("LOCK_OK",SPEC["checkpoints_sha256"],flush=True)
actors={}
for key,cp in CKS.items():
 state=torch.load(cp,map_location="cpu",weights_only=False)
 actor=LocalActor(hidden=state["config"]["hidden"])
 actor.load_state_dict(state["actor"])
 actor.eval()
 actors[key]=actor

@torch.no_grad()
def run_case(n,rows,cols,batch,steps,k,seed,mode):
 torch.manual_seed(seed+len(mode)*7)
 soc=VectorSociety(Configuration(rows=rows,cols=cols,batch=batch,
                                  seed=seed,randomize_majority=True))
 soc.reset(k=k)
 baseline=soc.tv().clone()
 tv=[baseline]
 churn=[]
 sends=[]
 accepts=[]
 incoming_max=0
 actor=actors["team_only"] if mode=="team_stochastic" else actors["credit_difference"]
 for t in range(steps):
  if mode=="no_previous_feedback":soc.feedback.zero_()
  obs=soc.observe()
  valid=soc.send_mask()
  if mode=="stay":
   msg=torch.zeros(batch,n,dtype=torch.long)
   incoming,req,sender=soc.deliveries(obs,msg)
   acc=torch.zeros_like(msg)
  else:
   baseline_random=(mode=="random")
   deterministic=(mode=="difference_deterministic")
   msg,_,_,emb=actor.sample_sender(obs,valid,
         deterministic=deterministic,random_baseline=baseline_random)
   if mode=="one_sender":
    only=torch.zeros_like(msg)
    only[:,0]=msg[:,0]
    msg=only
   incoming,req,sender=soc.deliveries(obs,msg)
   if mode=="strip_snapshot":sender=torch.zeros_like(sender)
   acc,_,_=actor.sample_receiver(emb,sender,incoming,req,
         deterministic=deterministic,random_baseline=baseline_random)
  incoming_max=max(incoming_max,int(incoming.sum(-1).max()))
  outcome=soc.step(msg,acc,incoming,req)
  tv.append(outcome["tv"].detach().clone())
  churn.append(outcome["churn"].detach().clone())
  sends.append(outcome["messages"].detach().clone())
  accepts.append(outcome["acceptances"].detach().clone())
 series=torch.stack(tv)
 cn=torch.stack(churn)
 st=((series[-10:]<=.06)&(cn[-10:]<=.05)).all(0)
 final=series[-1]
 return {"n":n,"k":k,"batch":batch,"steps":steps,
  "condition":mode,"seed":seed,
  "initial_tv":baseline.tolist(),
  "final_tv":final.tolist(),
  "last10_tv_each_world":series[-10:].mean(0).tolist(),
  "last10_churn_each_world":cn[-10:].mean(0).tolist(),
  "stable_final":st.tolist(),
  "exact_final":(final.abs()<1e-6).tolist(),
  "ever_below_006":(series<=.06).any(0).tolist(),
  "final_below_006":(final<=.06).tolist(),
  "mean_initial_tv":float(baseline.mean()),
  "mean_final_tv":float(final.mean()),
  "mean_last10_tv":float(series[-10:].mean()),
  "mean_final10_churn":float(cn[-10:].mean()),
  "frac_stable":float(st.float().mean()),
  "frac_final_below_006":float((final<=.06).float().mean()),
  "frac_exact":float((final.abs()<1e-6).float().mean()),
  "frac_ever_below_006":float((series<=.06).any(0).float().mean()),
  "mean_send_rate":float(torch.stack(sends).mean()),
  "mean_accept_rate":float(torch.stack(accepts).mean()),
  "max_received_requests":incoming_max,
  "tv_curve_mean":[float(z) for z in series.mean(1)],
  "churn_curve_mean":[float(z) for z in cn.mean(1)]}

def main():
 t0=time.perf_counter()
 res=[]
 for label,config in (("N36",SPEC["N36"]),("N120",SPEC["N120"])):
  rows,cols=config["rows"],config["cols"]
  for k in config["k"]:
   seed=(940000 if label=="N36" else 950000)+100*k
   for mode in config["conditions"]:
    path=OUT/f"{label}_k{k}_{mode}.json"
    if path.exists():raise RuntimeError("Already evaluated; do not overwrite "+str(path))
    case=run_case(rows*cols,rows,cols,config["batch"],config["steps"],k,seed,mode)
    path.write_text(json.dumps(case,indent=2,ensure_ascii=False),encoding="utf-8")
    res.append({key:val for key,val in case.items() if key not in
         ("initial_tv","final_tv","last10_tv_each_world","last10_churn_each_world",
          "stable_final","exact_final","ever_below_006","final_below_006",
          "tv_curve_mean","churn_curve_mean")})
    print("HELDOUT",label,"k",k,mode,
        "D",round(case["mean_final_tv"],4),
        "churn",round(case["mean_final10_churn"],4),
        "stable",round(case["frac_stable"],3),
        "exact",round(case["frac_exact"],3),
        "sent",round(case["mean_send_rate"],3),
        "elapsed",round(time.perf_counter()-t0,1),flush=True)
 output={"lock":SPEC,"summary":res,"n_cases":len(res),
         "test_not_used_for_model_selection":True,
         "limits":["one independent training cohort per treatment",
                   "episodes within one checkpoint are not independent training replications",
                   "same k values and architecture as training; transfer to N120 only",
                   "ablation of observation channels can induce distribution shift"]}
 path=OUT/"HOLDOUT_SUMMARY.json"
 if path.exists():raise RuntimeError("Duplicate summary")
 path.write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding="utf-8")
 print("HOLDOUT_DONE",len(res),"cases",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
