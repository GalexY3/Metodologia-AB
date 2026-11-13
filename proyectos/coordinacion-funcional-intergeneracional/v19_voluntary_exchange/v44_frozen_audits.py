"""V44 frozen six-environment evaluation and individual matched intervention.

Six holdout seeds were selected before final evaluations; no automatic
cooperation norms, no contract execution or cross-agent parameter sharing.
"""
from __future__ import annotations
import argparse,json,math,time
from pathlib import Path
import numpy as np,torch
from v44_private_dyads import (N,COST,BASE,MAX_STEPS,PrivateDyadic,
                               simulation)
ROOT=Path(__file__).resolve().parent
SEEDS=(980101,980107,980109,980121,980131,980137)
CONFIGS=("LONG_SOC","LONG_NOSOC","SHORT_SOC","SHORT_NOSOC")

def load(name,device):
 folder=ROOT/"runs"/name
 spec=json.loads((folder/"v44_spec.json").read_text("utf8"))
 status=json.loads((folder/"v44_status.json").read_text("utf8"))
 checkpoint=torch.load(folder/"dyadic_latest.pt",map_location="cpu",weights_only=False)
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==checkpoint["update"]
 actor=PrivateDyadic().to(device)
 actor.load_state_dict(checkpoint["actor"])
 actor.eval().requires_grad_(False)
 return actor,spec

@torch.no_grad()
def policy_sensitivity(actor,info,device):
 zeros=torch.zeros(1,N,device=device)
 ones=torch.ones_like(zeros)
 lastfood=torch.full_like(zeros,BASE)
 p0=torch.sigmoid(actor.logits(zeros,zeros,lastfood,False,info))
 p1=torch.sigmoid(actor.logits(zeros,ones,lastfood,False,info))
 difference=(p1-p0).flatten().cpu().numpy()
 if not info:assert (difference==0).all()
 return dict(mean=float(difference.mean()),
   positive=int((difference>1e-4).sum()),
   by_agent=difference.tolist())

@torch.no_grad()
def holdout(name,worlds,device):
 actor,spec=load(name,device)
 result=[]
 for seed in SEEDS:
  m,*_=simulation(actor,seed,batch=worlds,
     q=spec["q"],see_partner=spec["partner_info"]=="yes",device=device)
  result.append(dict(seed=seed,**m))
 metrics=("food","gifts","mutual","lifetime")
 rows=dict(model=name,seeds=list(SEEDS),worlds_per_seed=worlds,
   spec=spec,by_seed=result,
   metrics={k:float(np.mean([x[k] for x in result])) for k in metrics},
   sensitivity=policy_sensitivity(actor,spec["partner_info"]=="yes",device))
 p=ROOT/"results"/("v44_holdout_"+name+".json")
 p.write_text(json.dumps(rows,indent=1),encoding="utf8")
 print("V44_HOLDOUT",name,
   "FOOD",round(rows["metrics"]["food"],4),
   "GIFTS",round(rows["metrics"]["gifts"],4),
   "MUTUAL",round(rows["metrics"]["mutual"],4),
   "RESPONSE",round(rows["sensitivity"]["mean"],4),flush=True)
 return rows

@torch.no_grad()
def force_one(actor,seed,worlds,q,see_partner,device,forced):
 assert forced in (0,1)
 batch=worlds*N
 subjects=torch.arange(N,device=device).repeat(worlds)
 res,reward,_,_=simulation(actor,seed,batch=batch,q=q,
  see_partner=see_partner,device=device,
  forced_subject=subjects,force_t0=forced,
  survival_worlds=worlds)
 t=torch.arange(reward.shape[0],device=device)
 discount=torch.pow(torch.tensor(.995,device=device),t)[:,None]
 own=reward[:,torch.arange(batch,device=device),subjects]
 total=(own*discount).sum(0)
 initial=own[0]
 future=total-initial
 extract=lambda x:x.reshape(worlds,N).detach().cpu().numpy()
 return dict(total=extract(total),initial=extract(initial),
     future=extract(future))

@torch.no_grad()
def causal(name,worlds,device):
 actor,spec=load(name,device)
 rows=[]
 for seed in SEEDS:
  left=force_one(actor,seed,worlds,spec["q"],
   spec["partner_info"]=="yes",device,0)
  right=force_one(actor,seed,worlds,spec["q"],
   spec["partner_info"]=="yes",device,1)
  change={key:right[key]-left[key] for key in left}
  assert np.allclose(change["initial"],-COST,atol=1e-5),str((name,seed,change["initial"].min(),change["initial"].max()))
  rows.append(dict(seed=seed,per_agent={
   k:v.mean(0).tolist() for k,v in change.items()}))
 totals=np.asarray([x["per_agent"]["total"] for x in rows])
 immed=np.asarray([x["per_agent"]["initial"] for x in rows])
 output=dict(model=name,seeds=SEEDS,worlds_per_seed=worlds,
  spec=spec,by_seed=rows,
  mean_total=float(totals.mean()),
  mean_immediate=float(immed.mean()),
  mean_future=float(totals.mean()-immed.mean()),
  positive_agents=int((totals.mean(0)>0).sum()),
  per_agent=totals.mean(0).tolist(),
  matched_termination=True)
 (ROOT/"results"/("v44_causal_"+name+".json")).write_text(
  json.dumps(output,indent=1),encoding="utf8")
 print("V44_CAUSAL",name,"TOTAL",round(output["mean_total"],4),
   "FUTURE",round(output["mean_future"],4),
   "POS",output["positive_agents"],"/",N,flush=True)
 return output

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--kind",choices=("holdout","causal"),required=True)
 p.add_argument("--worlds",type=int,default=32)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 a=p.parse_args()
 torch.set_num_threads(2)
 t0=time.perf_counter()
 if a.kind=="holdout":holdout(a.name,a.worlds,a.device)
 else:causal(a.name,a.worlds,a.device)
 print("V44_AUDIT_DONE",a.name,a.kind,round(time.perf_counter()-t0,1),flush=True)

if __name__=="__main__":main()
