"""V47 frozen policies evaluated on 12 partner-reshuffle seeds and MC holdouts.

Personal policy weights remain frozen; pair identifiers change only in the
evaluation. Independent Monte Carlo uses V46's separate NumPy implementation.
"""
from __future__ import annotations
import argparse,json,torch,numpy as np
from pathlib import Path
from v46_exact_opponent_shaping import N,measurements
from v46_frozen_audits import run_episode_population
ROOT=Path(__file__).resolve().parent
PAIRING_SEEDS=(992101,992107,992109,992121,992131,992137,
 992141,992149,992153,992159,992163,992171)
ENV_SEEDS=(993101,993107,993109,993121,993131,993137)
MC_PAIRING_INDICES=(0,6)

def load(name):
 folder=ROOT/"runs"/name
 spec=json.loads((folder/"v47_spec.json").read_text("utf8"))
 status=json.loads((folder/"v47_status.json").read_text("utf8"))
 ck=torch.load(folder/"v47_latest.pt",map_location="cpu",weights_only=False)
 assert status["state"]=="completed" and ck["update"]==spec["updates"]==1000
 assert spec["n"]==48 and spec["q"]==.95
 return ck["logits"].detach().double(),spec

@torch.no_grad()
def evaluate(name,worlds=128):
 torch.set_num_threads(2)
 logits,spec=load(name)
 rows=[]
 for ind,seed in enumerate(PAIRING_SEEDS):
  index=np.random.default_rng(seed).permutation(N)
  current=logits[index]
  metrics=measurements(current,q=spec["q"])
  observed=[]
  if ind in MC_PAIRING_INDICES:
   for env in ENV_SEEDS:
    record=run_episode_population(current,spec["q"],env,worlds)
    observed.append(record)
   for metric,exact in (("food",metrics["food"]),
     ("mutual",metrics["mutual"]),("gifts",metrics["gifts"])):
    mean=float(np.mean([x[metric] for x in observed]))
    assert abs(mean-exact)<.015,(name,seed,metric,mean,exact)
  rows.append(dict(index=ind,pairing_seed=seed,
    food=metrics["food"],mutual=metrics["mutual"],donations=metrics["gifts"],
    causal=metrics["causal"],positive_agents=metrics["positive_agents"],
    causal_by_agent_original_index=dict(zip([int(x) for x in index],
      metrics["causal_agents"])),mc_environment_holdouts=observed))
 agg={key:float(np.mean([r[key] for r in rows]))
    for key in ("food","mutual","donations","causal","positive_agents")}
 agg["fraction_positive24_and_mutual25"]=float(np.mean([
    r["positive_agents"]>=24 and r["mutual"]>.25 for r in rows]))
 agg["min_positive_agents"]=min(r["positive_agents"] for r in rows)
 agg["max_positive_agents"]=max(r["positive_agents"] for r in rows)
 output=dict(name=name,spec=spec,partner_seeds=PAIRING_SEEDS,
   heldout_environment_seeds=ENV_SEEDS,
   mc_worlds_per_seed=worlds,
   monte_carlo_pairing_indices=MC_PAIRING_INDICES,
   rows=rows,aggregate=agg,
   note="partners reshuffled between episodes; only two people per simultaneous interaction")
 (ROOT/"results"/("v47_holdout_"+name+".json")).write_text(json.dumps(
   output,indent=1),encoding="utf8")
 print("V47_HOLDOUT_DONE",name,
    "food",round(agg["food"],4),
    "mutual",round(agg["mutual"],4),
    "causal",round(agg["causal"],4),
    "pos",round(agg["positive_agents"],2),
    "fraction",round(agg["fraction_positive24_and_mutual25"],3),flush=True)
 return output

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=128)
 a=p.parse_args()
 evaluate(a.name,a.worlds)
if __name__=="__main__":main()
