"""V46 frozen exact + environment holdout + randomized partner reassignment.

Analytic exact intervention is independent of Monte Carlo approximation.
All held-out environment and pairing seeds preregistered in AMENDMENT_V46.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,torch
from v46_exact_opponent_shaping import (N,B,V,C,GAMMA,H,measurements,expected)
ROOT=Path(__file__).resolve().parent
SEEDS=(990101,990107,990109,990121,990131,990137)
PAIRING_SEEDS=(991101,991107,991109,991121,991131,991137,
 991141,991149,991153,991159,991163,991171)

def load(name):
 path=ROOT/"runs"/name
 settings=json.loads((path/"v46_spec.json").read_text("utf8"))
 status=json.loads((path/"v46_status.json").read_text("utf8"))
 ck=torch.load(path/"v46_latest.pt",map_location="cpu",weights_only=False)
 assert status["state"]=="completed" and ck["update"]==settings["updates"]==1000
 logits=ck["logits"].detach().double()
 assert logits.shape==(N,5)
 return logits,settings

def run_episode_population(logits,q,seed,worlds):
 """NumPy implemention of a world of 24 independent pairs.

 This implementation is distinct from the torch Markov analytical solution,
 with shared termination across all 48 participants within a world.
 """
 assert logits.shape==(N,5)
 rng=np.random.default_rng(seed)
 expit=lambda a:1/(1+np.exp(-a))
 probs=expit(logits.detach().numpy())
 partner=np.arange(N)^1
 last=np.zeros((worlds,N),dtype=np.int64)
 alive=np.ones(worlds,dtype=bool)
 aggregate=dict(food=0.,gift=0.,mutual=0.,rounds=0.)
 for t in range(H):
  if t>0 and q<1:
   alive &= rng.random(worlds)<q
  count=int(alive.sum())
  if not count:break
  if t==0:
   p=np.broadcast_to(probs[:,0],(worlds,N))
  else:
   idx=1+last*2+last[:,partner]
   p=np.take_along_axis(np.broadcast_to(probs,(worlds,N,5)),
      idx[:,:,None],axis=2).squeeze(2)
  action=(rng.random((worlds,N))<p).astype(np.float64)
  food=B+V*action[:,partner]-C*action
  aggregate["food"]+=float(food[alive].sum())
  aggregate["gift"]+=float(action[alive].sum())
  aggregate["mutual"]+=float((action[:,partner]*action)[alive].sum())
  aggregate["rounds"]+=count
  last=action.astype(np.int64)
 divisor=N*aggregate["rounds"]
 return dict(seed=seed,worlds=worlds,
  mean_lifetime=aggregate["rounds"]/worlds,
  food=aggregate["food"]/divisor,
  gifts=aggregate["gift"]/divisor,
  mutual=aggregate["mutual"]/divisor)

@torch.no_grad()
def audit(name,worlds=128):
 torch.set_num_threads(2)
 logits,spec=load(name)
 q=spec["q"]
 primary=measurements(logits,q=q)
 simulation=[run_episode_population(logits,q,seed,worlds) for seed in SEEDS]
 mc={m:float(np.mean([x[m] for x in simulation]))
     for m in ("food","gifts","mutual","mean_lifetime")}
 agreement={k:abs(primary[k]-mc[k]) for k in ("food","gifts","mutual")}
 assert max(agreement.values())<.015,(name,agreement)
 reassignment=[]
 for seed in PAIRING_SEEDS:
  perm=np.random.default_rng(seed).permutation(N)
  rotated=logits[perm]
  snap=measurements(rotated,q=q)
  reassignment.append(dict(seed=seed,food=snap["food"],
    donations=snap["gifts"],mutual=snap["mutual"],
    causal=snap["causal"],
    positive_agents=snap["positive_agents"],
    per_agent_causal=snap["causal_agents"]))
 output=dict(model=name,spec=spec,
    analytic=primary,
    holdout_environment_seeds=SEEDS,
    holdout_worlds_per_seed=worlds,
    mc=mc,
    monte_carlo_by_seed=simulation,
    monte_carlo_discrepancies=agreement,
    transfer_seeds=PAIRING_SEEDS,
    transfer=reassignment,
    transfer_mean={key:float(np.mean([x[key] for x in reassignment]))
      for key in ("food","donations","mutual","causal","positive_agents")},
    transfer_fraction_with_24_positive=float(np.mean([
      x["positive_agents"]>=24 for x in reassignment])),
    difference_in_adaptation="none: all agent parameters frozen",
    evaluation_causal_type="first gift yes vs no, finite-horizon exact expected own payoff")
 file=ROOT/"results"/("v46_audit_"+name+".json")
 file.write_text(json.dumps(output,indent=1),encoding="utf8")
 print("V46_AUDIT_DONE",name,"EXACT_food",round(primary["food"],4),
   "MONTEfood",round(mc["food"],4),
   "EXACTcausal",round(primary["causal"],4),
   "POS",primary["positive_agents"],
   "TRANSFER_POS",round(output["transfer_mean"]["positive_agents"],2),
   "TRANSFER_MUTUAL",round(output["transfer_mean"]["mutual"],4),flush=True)
 return output

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=128)
 a=p.parse_args()
 audit(a.name,a.worlds)
if __name__=="__main__":main()
