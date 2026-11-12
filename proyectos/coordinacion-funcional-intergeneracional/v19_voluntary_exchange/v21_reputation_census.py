"""V21 full-population causal ablation of public reputation vs private receipts.

Paired 24-agent interventions for each fixed environment and checkpoint.
Replicates the V20 census in an actor with exactly the same policy weights,
but removes one observational channel at a time.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import torch,numpy as np
from targeted_gifts import C
from audit_targeted import load,SEEDS
from v20_all_agents_causal import forced
from v20_mechanism_ablation import FeatureAblatedActor

ROOT=Path(__file__).resolve().parent
MODES=("normal","no_direct_identity","no_public_offer",
       "no_own_target_memory","no_both_except_receipt","no_social")
SCENARIOS=((2,2,"ring"),(2,2,"rewired"),(3,2,"ring"))
@torch.no_grad()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=24)
 p.add_argument("--steps",type=int,default=48)
 p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 a=p.parse_args()
 torch.set_num_threads(2)
 old,spec,u=load(a.name,a.device)
 actor=FeatureAblatedActor(spec["n"],spec["hidden"],spec["init_scale"]).to(a.device)
 actor.load_state_dict(old.state_dict());actor.eval()
 t0=time.perf_counter()
 rows=[]
 for k,degree,topology in SCENARIOS:
  c=C(n=spec["n"],k=k,degree=degree,topology=topology,
      batch=a.worlds,horizon=a.steps,cost=spec["cost"],
      gamma=spec["gamma"],device=a.device)
  for mode in MODES:
   by_seed=[]
   for seed in SEEDS:
    yes=forced(c,actor,seed,mode,1)
    no=forced(c,actor,seed,mode,0)
    delta={key:yes[key]-no[key] for key in yes if yes[key] is not None}
    by_seed.append(dict(seed=seed,
       per_agent_total=delta["total"].mean(0).tolist(),
       per_agent_immediate=delta["immediate"].mean(0).tolist(),
       per_agent_next_incoming=delta["next_incoming"].mean(0).tolist()))
   z=np.asarray([v["per_agent_total"] for v in by_seed])
   row=dict(k=k,degree=degree,topology=topology,mode=mode,
      worlds=c.batch*len(SEEDS),agents=c.n,
      mean_total=float(z.mean()),even=float(z[:,::2].mean()),
      odd=float(z[:,1::2].mean()),
      positive_agents=int((z.mean(0)>0).sum()),
      positive_seed_agent_pairs=int((z>0).sum()),
      seed_agent_pairs=int(z.size),
      mean_by_agent=z.mean(0).tolist(),by_seed=by_seed)
   rows.append(row)
   print("V21_REP",a.name,k,topology,mode,
         "return",round(row["mean_total"],4),
         "positive",row["positive_agents"],"of",c.n,
         "runtime",round(time.perf_counter()-t0,1),flush=True)
 data=dict(model=a.name,checkpoint=u,worlds_per_seed=a.worlds,
           environmental_seeds=SEEDS,steps=a.steps,rows=rows,
           method="Counterfactual forced donation, all private actors, identity-specific channel removal.")
 path=ROOT/"results"/("v21_reputation_"+a.name+".json")
 path.write_text(json.dumps(data,indent=1),encoding="utf8")
 print("V21_REP_FINISHED",a.name,len(rows),flush=True)

if __name__=="__main__":main()
