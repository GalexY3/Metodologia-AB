"""V10C: blind-to-repair selection of physically identical 50% neuronal masks
whose immediate validation damage is comparable across the two training histories.
Mask candidates 1001..2000 are NEW relative to V10B. No repair is run here.
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
import torch
from parity_v10 import MLP,data
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)
x,y,ids=data(20261109,500,1000,2000)
xx=x[ids["val"]]; yy=y[ids["val"]]
SEEDS=list(range(1001,2001))
masks=[]
for ms in SEEDS:
 rng=np.random.default_rng(ms)
 idx=sorted(rng.choice(300,150,replace=False).tolist())
 surviving=np.ones(300,dtype=np.float32)
 surviving[idx]=0.
 masks.append(surviving)
stack=torch.from_numpy(np.stack(masks)).T.contiguous()
allresults=[]
for seed in range(5):
 bylam={}
 for lam in (1e-5,.001):
  name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
  ck=torch.load(ROOT/"parity_runs"/name/"ck_008000.pt",map_location="cpu",weights_only=False)
  net=MLP(300);net.load_state_dict(ck["model"])
  with torch.no_grad():
   h=torch.relu(net.a(xx))
   w=net.b.weight[1]-net.b.weight[0]
   intercept=net.b.bias[1]-net.b.bias[0]
   logits=h@(stack*w[:,None])+intercept
   pred=logits>0
   scores=(pred==yy[:,None].bool()).float().mean(0)
   initial=net(xx).argmax(1)
   assert float((initial==yy).float().mean())==1.
  damage=(1-scores)*100.
  bylam[str(lam)]=[round(float(v),5) for v in damage.tolist()]
 rows=[]
 for i,ms in enumerate(SEEDS):
  a=bylam[str(1e-5)][i]
  b=bylam[str(.001)][i]
  accepted=(10<=a<=40 and 10<=b<=40 and abs(a-b)<=5)
  rows.append({"mask":ms,"damage_grok_pp":a,"damage_continuous_pp":b,"abs_difference_pp":round(abs(a-b),5),"eligible":accepted})
 chosen=[v for v in rows if v["eligible"]][:5]
 item={"seed":seed,"candidate_count":len(rows),"accepted_count":sum(v["eligible"] for v in rows),
       "selected_first5":chosen,"all_candidates":rows}
 allresults.append(item)
 print("MASK_SCAN",seed,"eligible",item["accepted_count"],"selected",json.dumps(chosen),flush=True)
out={"status":"post_hoc damage-matched exploratory; no repair outcomes consulted",
     "protocol":"PREREG_V10C.md","mask_seed_range":[1001,2000],"dose":150,"thresholds":{"min_damage":10,"max_damage":40,"max_gap":5},"per_seed":allresults}
(ROOT/"V10C_MASK_SCAN.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
