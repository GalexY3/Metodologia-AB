"""Behavioral interpretation of the trained agents, no parameter updates.

Quantify sender/receiver behavior, role switching, local relative abundance,
global marginal contribution (ANALYST ONLY), edge/interior opportunity, and
repeatability of apparent spatial roles. Compared to an always-random policy.
"""
from pathlib import Path
import json,time,hashlib
import numpy as np
import torch
import torch.nn.functional as F
from environment import VectorSociety,Configuration
from agents import LocalActor

torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"behavior_v2d";OUT.mkdir(exist_ok=True)
SEEDS=(221,223)
KS=(2,3,4)
WORLD_BATCH=8
TICKS=90

def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
ck={s:ROOT/"runs"/f"credit2_seed{s}_u180"/"checkpoint_0180.pt" for s in SEEDS}
lock={"protocol":"PREREG_SCALE_STRATEGY_AUDIT.md",
 "model":sha(ROOT/"agents.py"),"environment":sha(ROOT/"environment.py"),
 "script":sha(ROOT/"behavior_v2d.py"),
 "weights":{str(s):sha(p) for s,p in ck.items()},
 "training_seeds":list(SEEDS),"k":list(KS),"n":120,"worlds":WORLD_BATCH,
 "ticks":TICKS,"modes":["learned","random"],
 "world_seed":"1510000+1000*model_seed+100*k"}
path=OUT/"TEST_LOCK.json"
if path.exists():
 if json.loads(path.read_text(encoding="utf-8"))!=lock:raise RuntimeError("Code or model not locked")
else:path.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
models={}
for seed,p in ck.items():
 obj=torch.load(p,map_location="cpu",weights_only=False)
 actor=LocalActor(hidden=obj["config"]["hidden"])
 actor.load_state_dict(obj["actor"]);actor.eval()
 models[seed]=actor

def corr(a,b):
 a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
 if a.std()<1e-9 or b.std()<1e-9:return None
 return float(np.corrcoef(a,b)[0,1])

def gini(x):
 x=np.asarray(x,dtype=float)
 if x.sum()==0:return 0.
 xs=np.sort(x)
 n=len(x)
 return float((2*np.dot(np.arange(1,n+1),xs)/(n*xs.sum()))-(n+1)/n)

@torch.no_grad()
def simulate(seed,k,mode):
 actor=models[seed]
 batch=WORLD_BATCH
 world_seed=1510000+1000*seed+100*k
 torch.manual_seed(world_seed+41*(mode=="random"))
 env=VectorSociety(Configuration(rows=10,cols=12,batch=batch,
        seed=world_seed,randomize_majority=True))
 env.reset(k=k)
 N=env.n
 degrees=env.valid.sum(1).numpy()
 sender_site=np.zeros((batch,N),dtype=np.float64)
 received_site=np.zeros((batch,N),dtype=np.float64)
 accepted_site=np.zeros((batch,N),dtype=np.float64)
 changes_site=np.zeros((batch,N),dtype=np.float64)
 source_color_to_request=np.zeros((k,k),dtype=np.int64)
 origin_to_destination=np.zeros((k,k),dtype=np.int64)
 turn_period={key:{"sent":0,"accepted":0,"changed":0,"tv_sum":0.,
                   "positive_credit":0,"negative_credit":0,"zero_credit":0,
                   "requests":0,"messages":0} for key in ("early","middle","late")}
 requested_rare=0
 requested_overall=0
 requested_deficit=0
 beneficial_count=0;harmful_count=0;neutral_count=0
 changes=0;agreements=0
 sent_total=0;received_total=0
 color_equal_requests=0
 local_rare_all=0
 mean_tv=[]
 for t in range(TICKS):
  old=env.colors.clone()
  obs=env.observe()
  send,_,_,z=actor.sample_sender(obs,env.send_mask(),random_baseline=mode=="random")
  incoming,requested,snapshot=env.deliveries(obs,send)
  accept,_,_=actor.sample_receiver(z,snapshot,incoming,requested,
                                   random_baseline=mode=="random")
  outcome=env.step(send,accept,incoming,requested)
  new=env.colors
  bsend=send>0
  bacc=accept>0
  bchg=new!=old
  sender_site+=bsend.numpy()
  received_site+=incoming.sum(-1).numpy()
  accepted_site+=bacc.numpy()
  changes_site+=bchg.numpy()
  sent_total+=int(bsend.sum())
  received_total+=int(incoming.sum())
  agreements+=int(bacc.sum())
  changes+=int(bchg.sum())
  choose=((send-1).clamp(min=0)%4)
  hist_global=F.one_hot(old,4).sum(1)
  request_deficit=hist_global.gather(1,choose)<(N/k)
  requested_deficit+=int((request_deficit&bsend).sum())
  local=F.one_hot(old[:,env.neighbors],4).float()*env.valid[None,:,:,None]
  freq=local.sum(2)
  frequency_req=freq.gather(-1,choose.unsqueeze(-1)).squeeze(-1)
  minority=(frequency_req==freq[:,:,:k].min(-1).values)&bsend
  requested_rare+=int(minority.sum())
  requested_overall+=int(bsend.sum())
  color_equal_requests+=int(((old==choose)&bsend).sum())
  for source in range(k):
   for dest in range(k):
    source_color_to_request[source,dest]+=int(((old==source)&(choose==dest)&bsend).sum())
    origin_to_destination[source,dest]+=int(((old==source)&(new==dest)&bchg).sum())
  period="early" if t<30 else ("middle" if t<60 else "late")
  tt=turn_period[period]
  tt["sent"]+=int(bsend.sum())
  tt["accepted"]+=int(bacc.sum())
  tt["changed"]+=int(bchg.sum())
  tt["tv_sum"]+=float(outcome["tv"].sum())
  tt["messages"]+=1
  tt["requests"]+=int(incoming.sum())
  # Calculate exact marginal impact of each actual change on final TV,
  # with all other changes held fixed. It is ANALYST-ONLY, never action input.
  counts=F.one_hot(new,4).float().sum(1)
  cf_counts=counts[:,None,:]+F.one_hot(old,4).float()-F.one_hot(new,4).float()
  target=torch.full((1,1,k),N/k)
  dc=.5*((cf_counts[:,:,:k]/N-1/k).abs()).sum(-1)
  actual=outcome["tv"][:,None]
  marginal=N*(dc-actual)
  beneficial_count+=int(((marginal>1e-5)&bchg).sum())
  harmful_count+=int(((marginal< -1e-5)&bchg).sum())
  neutral_count+=int(((marginal.abs()<=1e-5)&bchg).sum())
  tt["positive_credit"]+=int(((marginal>1e-5)&bchg).sum())
  tt["negative_credit"]+=int(((marginal<-1e-5)&bchg).sum())
  tt["zero_credit"]+=int(((marginal.abs()<=1e-5)&bchg).sum())
  mean_tv.append(float(outcome["tv"].mean()))

 # Node-level persistent engagement over episodes. All nodes share weights:
 # structural roles may arise from degree and position, not identities.
 sender_rate=sender_site/TICKS
 reception_rate=received_site/TICKS
 accept_rate=accepted_site/TICKS
 change_rate=changes_site/TICKS
 bydegree=[]
 for d in sorted(set(degrees)):
  nsites=int(np.sum(degrees==d))
  bydegree.append({"degree":int(d),"nodes_per_world":nsites,
     "send_per_node_turn":float(sender_rate[:,degrees==d].mean()),
     "received_per_node_turn":float(reception_rate[:,degrees==d].mean()),
     "accept_per_node_turn":float(accept_rate[:,degrees==d].mean()),
     "change_per_node_turn":float(change_rate[:,degrees==d].mean())})
 half=WORLD_BATCH//2
 within_corr=corr(sender_rate[:half].mean(0),sender_rate[half:].mean(0))
 residual=sender_rate.copy()
 for d in set(degrees):
  residual[:,degrees==d]-=sender_rate[:,degrees==d].mean(axis=1,keepdims=True)
 residual_corr=corr(residual[:half].mean(0),residual[half:].mean(0))
 total=batch*N*TICKS
 return {"seed":seed,"k":k,"mode":mode,
    "societies":batch,"n_agents":N,"ticks":TICKS,
    "final_tv":float(mean_tv[-1]),
    "mean_last10_tv":float(np.mean(mean_tv[-10:])),
    "mean_send_rate":sent_total/total,
    "mean_received_per_agent_turn":received_total/total,
    "mean_accept_rate":agreements/total,
    "mean_actual_change_rate":changes/total,
    "acceptance_rate_per_incoming":agreements/received_total if received_total else None,
    "change_per_accepted_request":changes/agreements if agreements else None,
    "request_target_global_deficit_fraction":requested_deficit/requested_overall if requested_overall else None,
    "request_target_local_minimum_fraction":requested_rare/requested_overall if requested_overall else None,
    "requests_that_repeat_sender_own_color_fraction":color_equal_requests/requested_overall if requested_overall else None,
    "positive_impact_changes_fraction":beneficial_count/changes if changes else None,
    "negative_impact_changes_fraction":harmful_count/changes if changes else None,
    "neutral_impact_changes_fraction":neutral_count/changes if changes else None,
    "origin_color_by_requested_color":source_color_to_request.tolist(),
    "origin_color_by_actual_new_color":origin_to_destination.tolist(),
    "epoch":{p:{"send_rate":z["sent"]/(30*batch*N),
      "accept_rate":z["accepted"]/(30*batch*N),
      "change_rate":z["changed"]/(30*batch*N),
      "mean_tv":z["tv_sum"]/(30*batch),
      "beneficial_changes":z["positive_credit"],
      "harmful_changes":z["negative_credit"]} for p,z in turn_period.items()},
    "degree_roles":bydegree,
    "sender_engagement_gini_per_world":[gini(v) for v in sender_site],
    "sender_engagement_gini_mean":float(np.mean([gini(v) for v in sender_site])),
    "spatial_sender_role_consistency_between_world_halves":within_corr,
    "residual_sender_role_consistency_after_degree":residual_corr,
    "interpretation_limits":["all agents share SAME neural policy weights",
      "roles can reflect observations, graph position, and random trajectory; not permanent social classes",
      "global deficits and marginal impacts are computed by analyst after actions only"]}

def main():
 start=time.perf_counter()
 summaries=[]
 for seed in SEEDS:
  for k in KS:
   for mode in ("learned","random"):
    path=OUT/f"seed{seed}_k{k}_{mode}.json"
    if path.exists():raise RuntimeError("Refusing overwrite "+str(path))
    z=simulate(seed,k,mode)
    path.write_text(json.dumps(z,ensure_ascii=False,indent=2),encoding="utf-8")
    summaries.append({name:value for name,value in z.items()
      if name not in ("origin_color_by_requested_color","origin_color_by_actual_new_color",
                      "degree_roles","epoch","sender_engagement_gini_per_world",
                      "interpretation_limits")})
    print("BEHAVIOR",seed,k,mode,
          "TV",round(z["mean_last10_tv"],4),
          "send",round(z["mean_send_rate"],3),
          "accept",round(z["mean_accept_rate"],3),
          "churn",round(z["mean_actual_change_rate"],3),
          "requests_locally_rarest",round(z["request_target_local_minimum_fraction"],3),
          "positive_marginal",round(z["positive_impact_changes_fraction"],3) if z["positive_impact_changes_fraction"] is not None else "nan",
          "elapsed",round(time.perf_counter()-start,1),flush=True)
 (OUT/"SUMMARY.json").write_text(json.dumps({"lock":lock,
   "cases":summaries,"n_cases":len(summaries),
   "cautions":["one shared parameterized policy per learned cohort; any roles found are state or position dependent",
     "no causal human behavior implied", "analyst has global oracle but policy does not during execution"]},
     ensure_ascii=False,indent=2),encoding="utf-8")
 print("BEHAVIOR_DONE",len(summaries),"cases",round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":main()
