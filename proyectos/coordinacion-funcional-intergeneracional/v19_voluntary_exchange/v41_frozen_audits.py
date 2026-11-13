"""V41 frozen auditor: all-agent counterfactuals and matched social-signal controls.

Reuses V30 original frozen evaluator; adds explicitly social-suppressed
random occupation baselines to avoid comparing unlike observations for
V41 policies trained without any history signals.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from audit_targeted import SEEDS
from v25_holdout import load
import v30_frozen_audits as original
from v30_consensual import install,traced_roll
ROOT=Path(__file__).resolve().parent
METRICS=("food","final_food","gifts_per_person","distinct_coverage",
 "complete","potential_coverage","balanced","professions","switches",
 "proposals_per_person","settled_units_per_person",
 "acceptance_fraction","physical_useful_ratio")

@torch.no_grad()
def extra_unsocial_random(name,worlds,steps,device):
 donor,role,spec=load(name,device)
 path=ROOT/"results"/("v30_holdout_"+name+".json")
 data=json.loads(path.read_text("utf8"))
 assert len(data["rows"])==32
 for topo,init in (("ring","monolith"),("ring","random"),
  ("ring","balanced"),("rewired","monolith")):
  for tag in ("015","035","060"):
   per=[]
   rate={"015":.15,"035":.35,"060":.60}[tag]
   for seed in SEEDS:
    c=C(n=spec["n"],k=4,degree=6,topology=topo,
     batch=worlds,horizon=steps,cost=spec["cost"],
     gamma=spec["gamma"],device=device)
    torch.manual_seed(seed*73+41)
    measure,*_=traced_roll(c,donor,role,seed,
      init=init,interval=spec["role_interval"],
      move_cost=spec["move_cost"],social=False,
      baseline="random_"+str(rate))
    per.append(dict(seed=seed,**measure))
   data["rows"].append(dict(model=name,topology=topo,init=init,
       condition="role_random_nosoc_"+tag,worlds=worlds*len(SEEDS),
       **{k:float(np.mean([x[k] for x in per])) for k in METRICS},
       by_seed=per))
 assert len(data["rows"])==44
 path.write_text(json.dumps(data,indent=1),encoding="utf8")
 print("V41_NOSOC_ROLE_BASELINE",name,len(data["rows"]),flush=True)

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--name",required=True)
 parser.add_argument("--kind",choices=("holdout","causal"),required=True)
 parser.add_argument("--worlds",type=int,default=8)
 parser.add_argument("--steps",type=int,default=48)
 parser.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 a=parser.parse_args()
 spec=json.loads((ROOT/"runs"/a.name/"v41_spec.json").read_text("utf8"))
 assert spec["settlement"]=="unilateral" and spec["n"]==48
 torch.set_num_threads(2)
 install("unilateral")
 if a.kind=="causal":
  original.causal(a.name,worlds=a.worlds,horizon=a.steps,device=a.device)
 else:
  original.holdout(a.name,worlds=a.worlds,horizon=a.steps,device=a.device)
  if spec["social"]=="no":
   extra_unsocial_random(a.name,a.worlds,a.steps,a.device)
 print("V41_AUDIT_DONE",a.name,a.kind,flush=True)
if __name__=="__main__":main()
