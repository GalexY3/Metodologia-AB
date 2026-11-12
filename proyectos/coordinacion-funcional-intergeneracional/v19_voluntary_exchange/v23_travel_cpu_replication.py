"""V23 frozen CPU replication on an independent Windows computer.

Same versioned implementation and pretrained-from-scratch V23 checkpoint;
different CPU and PyTorch version, no training. Separate reproduction file
so published GPU measurements are never overwritten.
"""
from pathlib import Path
import json,time
import numpy as np,torch
from targeted_gifts import C
from v23_joint_audit import load_model,forced
from v23_joint_cold import roll
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(2)
t0=time.perf_counter();records=[]
for name in ("v23_SMOOTH_s3111","v23_SMOOTH_s4111"):
 donor,role,spec=load_model(name,"cpu")
 c=C(n=24,k=2,degree=2,topology="ring",batch=16,
      horizon=48,cost=spec["cost"],gamma=spec["gamma"],device="cpu")
 for social in (True,False):
  data=[]
  for seed in SEEDS:
   torch.manual_seed(seed*73+19)
   with torch.no_grad():
    m,*_=roll(c,donor,role,seed,init="monolith",
        social=social,interval=spec["role_interval"],
        switch_cost=spec["switch_cost"])
   data.append(dict(seed=seed,**m))
  row=dict(model=name,analysis="food",social=social,
       food=float(np.mean([x["mean_food"] for x in data])),
       gifts=float(np.mean([x["gift"] for x in data])),
       links=float(np.mean([x["complementary_links"] for x in data])),
       seeds=data,worlds=16)
  records.append(row)
  print("TRAVEL_V23",name,"food",social,round(row["food"],4),
        round(row["gifts"],4),flush=True)
 c2=C(n=24,k=2,degree=2,topology="ring",batch=4,
        horizon=48,cost=spec["cost"],gamma=spec["gamma"],device="cpu")
 for mode in ("normal","no_history"):
  diffs=[]
  for seed in SEEDS:
   yes=forced(c2,donor,role,seed,"monolith",mode,1,
       interval=spec["role_interval"],switch_cost=spec["switch_cost"])
   no=forced(c2,donor,role,seed,"monolith",mode,0,
       interval=spec["role_interval"],switch_cost=spec["switch_cost"])
   delta=yes["total"]-no["total"]
   immediate=yes["initial"]-no["initial"]
   assert np.allclose(immediate,-spec["cost"],atol=1e-5)
   diffs.append(dict(seed=seed,per_agent=delta.mean(0).tolist()))
  arr=np.array([r["per_agent"] for r in diffs])
  row=dict(model=name,analysis="causal",mode=mode,
     mean_return=float(arr.mean()),
     positive_agents=int((arr.mean(0)>0).sum()),
     worlds=4,seeds=diffs)
  records.append(row)
  print("TRAVEL_V23",name,"causal",mode,round(row["mean_return"],4),
      row["positive_agents"],"/24",flush=True)
out=dict(created="2026-11-12",
  source_commit="210fc99a880a745376a2f35ccf5ceecff42e0587",
  cpu_torch=torch.__version__,hardware="GalexY_travel CPU",
  methodological_note="Same source and trained checkpoint, distinct device and PyTorch runtime; no independent implementation. Different holdout world count (16 vs original 24) and causal world count (4 vs original 12).",
  elapsed=time.perf_counter()-t0,records=records)
(ROOT/"results"/"v23_travel_cpu_replication.json").write_text(
 json.dumps(out,indent=1),encoding="utf8")
print("TRAVEL_V23_DONE",len(records),"seconds",round(time.perf_counter()-t0,1),flush=True)
