"""Adversarial tests on the existing credit2 policy, N120, k4.

Pre-specified in PREREG_SCALE_STRATEGY_AUDIT.md. All interventions change
execution inputs/actions without retraining; report possible OOD caveats.
"""
from pathlib import Path
import json,hashlib,time
import torch
from environment import VectorSociety,Configuration
from agents import LocalActor

torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"ablations_v2d";OUT.mkdir(exist_ok=True)
SEEDS=(221,222,223)
CONDITIONS=("trained","no_sender_snapshot","no_direct_neighbor",
            "no_last_feedback","one_sender","random_T8","random_T24",
            "random_always","stay")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
checkpoints={z:ROOT/"runs"/f"credit2_seed{z}_u180"/"checkpoint_0180.pt" for z in SEEDS}
lock={"protocol":"PREREG_SCALE_STRATEGY_AUDIT.md",
      "script_sha":sha(ROOT/"adversarial_v2d.py"),
      "model_sha":sha(ROOT/"agents.py"),
      "env_sha":sha(ROOT/"environment.py"),
      "weights":{str(z):sha(p) for z,p in checkpoints.items()},
      "seeds":list(SEEDS),"k":4,"n":120,"batch":40,"steps":90,
      "world_seeds":"1310000+1000*training_seed+100*k",
      "conditions":list(CONDITIONS),"freeze_steps":[8,24]}
p=OUT/"TEST_LOCK.json"
if p.exists():
 if json.loads(p.read_text(encoding="utf-8"))!=lock:
  raise RuntimeError("Changed preregistered code/weights")
else:p.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
models={}
for z,path in checkpoints.items():
 s=torch.load(path,map_location="cpu",weights_only=False)
 net=LocalActor(hidden=s["config"]["hidden"])
 net.load_state_dict(s["actor"]);net.eval()
 models[z]=net

@torch.no_grad()
def case(trainseed,mode):
 n=120;steps=90;batch=40;k=4
 world=1310000+1000*trainseed+100*k
 torch.manual_seed(world+7*len(mode))
 env=VectorSociety(Configuration(rows=10,cols=12,batch=batch,
                                  seed=world,randomize_majority=True))
 env.reset(k=4)
 net=models[trainseed]
 tv=[env.tv().clone()]
 churn=[]
 messages=[]
 accepted=[]
 received=[]
 for t in range(steps):
  if mode=="no_last_feedback":env.feedback.zero_()
  obs=env.observe()
  if mode=="no_direct_neighbor":
   obs=obs.clone()
   obs[:,:,4:24]=0. # five one-hot neighbor slots, no color information
  use_random=mode in ("random_T8","random_T24","random_always")
  T=8 if mode=="random_T8" else (24 if mode=="random_T24" else 999)
  inactive=(mode=="stay") or (use_random and t>=T)
  if inactive:
   sends=torch.zeros(batch,n,dtype=torch.long)
   incoming,request,snapshot=env.deliveries(obs,sends)
   accept=torch.zeros_like(sends)
  else:
   sends,_,_,z=net.sample_sender(obs,env.send_mask(),random_baseline=use_random)
   if mode=="one_sender":
    clone=torch.zeros_like(sends);clone[:,0]=sends[:,0];sends=clone
   incoming,request,snapshot=env.deliveries(obs,sends)
   if mode=="no_sender_snapshot":snapshot=torch.zeros_like(snapshot)
   accept,_,_=net.sample_receiver(z,snapshot,incoming,request,random_baseline=use_random)
  metric=env.step(sends,accept,incoming,request)
  tv.append(metric["tv"].clone())
  churn.append(metric["churn"].clone())
  messages.append(metric["messages"].clone())
  accepted.append(metric["acceptances"].clone())
  received.append(float(metric["requests_received"].float().mean()))
 v=torch.stack(tv)
 c=torch.stack(churn)
 sustained=((v[-10:]<=.06)&(c[-10:]<=.05)).all(0)
 return {"trainseed":trainseed,"mode":mode,"world_seed":world,
 "n":n,"batch":batch,"k":k,"steps":steps,
 "mean_initial_tv":float(v[0].mean()),
 "mean_final_tv":float(v[-1].mean()),
 "mean_last10_tv":float(v[-10:].mean()),
 "mean_last10_churn":float(c[-10:].mean()),
 "stable_count":int(sustained.sum()),
 "stable_fraction":float(sustained.float().mean()),
 "near_final_count":int((v[-1]<=.06).sum()),
 "exact_final_count":int((v[-1].abs()<1e-6).sum()),
 "ever_near_count":int((v<=.06).any(0).sum()),
 "mean_request_send_fraction":float(torch.stack(messages).mean()),
 "mean_accept_fraction":float(torch.stack(accepted).mean()),
 "mean_requests_received":sum(received)/len(received),
 "tv_by_world_final":v[-1].tolist(),
 "stable_by_world":sustained.tolist(),
 "tv_curve_mean":[float(z) for z in v.mean(1)],
 "churn_curve_mean":[float(z) for z in c.mean(1)]}

def main():
 t0=time.perf_counter()
 out=[]
 for seed in SEEDS:
  for mode in CONDITIONS:
   path=OUT/f"seed{seed}_{mode}.json"
   if path.exists():raise RuntimeError("Existing result; refuse overwrite: "+str(path))
   q=case(seed,mode)
   path.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
   out.append({key:val for key,val in q.items() if key not in
              ("tv_by_world_final","stable_by_world","tv_curve_mean","churn_curve_mean")})
   print("ABLATE",seed,mode,"TV",round(q["mean_last10_tv"],4),
         "stable",q["stable_count"],"/40",
         "churn",round(q["mean_last10_churn"],4),
         "exact",q["exact_final_count"],
         "time",round(time.perf_counter()-t0,1),flush=True)
 (OUT/"SUMMARY.json").write_text(json.dumps({
    "lock":lock,"cases":out,"n_train_cohorts":len(SEEDS),
    "status":"all conditions specified before inspecting new outcome",
    "limits":["test of trained model under OOD ablations is not equivalent to independently optimized controls",
              "random_T8 and random_T24 use a researcher-defined shared stopping clock",
              "no counterfactual oracle used during evaluation"]},
    ensure_ascii=False,indent=2),encoding="utf-8")
 print("ABLATION_DONE",len(out),"case batches",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
