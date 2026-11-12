"""Independent-device CPU replay of V20 full-population counterfactuals.

Runs on GalexY_travel with its separate PyTorch CPU installation.
Loads the exact versioned commit 31d553db checkpoints and source code;
changes only device and evaluation batch count. This is a cross-hardware
reproduction, not independent source-code implementation.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import torch,numpy as np
from targeted_gifts import C
from audit_targeted import SEEDS,load
from v20_all_agents_causal import forced
from v20_mechanism_ablation import FeatureAblatedActor

ROOT=Path(__file__).resolve().parent
torch.set_num_threads(2)
out=[]
t0=time.perf_counter()
for name in ("v20_SMOOTH_s3111","v20_SMOOTH_s4111","v20_CONST_s3111"):
 src,spec,u=load(name,"cpu")
 actor=FeatureAblatedActor(spec["n"],spec["hidden"],spec["init_scale"]).cpu()
 actor.load_state_dict(src.state_dict());actor.eval()
 c=C(n=spec["n"],k=2,degree=2,topology="ring",batch=16,
   horizon=48,cost=spec["cost"],gamma=spec["gamma"],device="cpu")
 for mode in ("normal","no_direct_identity","no_public_offer","no_social"):
  series=[]
  for seed in SEEDS:
   yes=forced(c,actor,seed,mode,1)
   no=forced(c,actor,seed,mode,0)
   series.append((yes["total"]-no["total"]).mean(axis=0))
  arr=np.asarray(series)
  row=dict(model=name,seed_env=SEEDS,mode=mode,worlds=16,
    n_agents=c.n,mean=float(arr.mean()),
    pos_agents=int((arr.mean(axis=0)>0).sum()),
    per_agent=arr.mean(axis=0).tolist(),
    seed_agent_means=arr.tolist())
  out.append(row)
  print("TRAVEL_REPLAY",name,mode,"return",round(row["mean"],4),
        "positive_agents",row["pos_agents"],
        "elapsed",round(time.perf_counter()-t0,1),flush=True)
dest=ROOT/"results"/"v21_travel_cpu_replication.json"
dest.write_text(json.dumps(dict(
 created="2026-11-12",source_commit="31d553db871e18ac0266fdafdd1b7a23c223962e",
 python_torch=torch.__version__,device="cpu",
 caveat="Same source, separate device, different PyTorch version; evaluation batches of 16 instead of 24/32; not independent implementation.",
 rows=out),indent=1),encoding="utf8")
print("TRAVEL_REPLAY_DONE",len(out),"cases",round(time.perf_counter()-t0),flush=True)
