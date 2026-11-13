"""V53B factorial one-at-a-time material sensitivity with paired worlds."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
import v53_vsm_material as m
ROOT=Path(__file__).resolve().parent
BASE=dict(fees=dict(m.FEES),transfer_loss=m.TRANSFER_LOSS,
 initial=m.INITIAL,capacity=m.CAPACITY,subsistence=m.SUBSISTENCE)
VARIANTS=("BASE","HALF_ADMIN","ZERO_ADMIN","DOUBLE_ADMIN",
 "FREE_TRANSFER","LOSS20","LOW_SUBSISTENCE","HIGH_SUBSISTENCE",
 "SHORT_BUFFER","LONG_BUFFER")
GOVERNANCE=tuple(m.GOVERNANCE)
ENVIRONMENT=("PATCHY","SYSTEMIC")

def update(name):
 assert name in VARIANTS
 c=dict(BASE)
 c["fees"]=dict(BASE["fees"])
 if name=="HALF_ADMIN":c["fees"]={k:v*.5 for k,v in c["fees"].items()}
 if name=="ZERO_ADMIN":c["fees"]={k:0. for k in c["fees"]}
 if name=="DOUBLE_ADMIN":c["fees"]={k:v*2 for k,v in c["fees"].items()}
 if name=="FREE_TRANSFER":c["transfer_loss"]=0.
 if name=="LOSS20":c["transfer_loss"]=.20
 if name=="LOW_SUBSISTENCE":c["subsistence"]=.68
 if name=="HIGH_SUBSISTENCE":c["subsistence"]=.82
 if name=="SHORT_BUFFER":c["initial"]=.65;c["capacity"]=1.25
 if name=="LONG_BUFFER":c["initial"]=2.;c["capacity"]=3.
 assert c["initial"]<=c["capacity"]
 m.FEES=c["fees"]
 m.TRANSFER_LOSS=c["transfer_loss"]
 m.INITIAL=c["initial"]
 m.CAPACITY=c["capacity"]
 m.SUBSISTENCE=c["subsistence"]
 return c

def evaluate(worlds=128):
 data=[];start=time.perf_counter()
 for name in VARIANTS:
  parameters=update(name)
  for environment in ENVIRONMENT:
   for governance in GOVERNANCE:
    by_seed=[m.simulate(seed,worlds,environment,governance)
       for seed in m.SEEDS]
    metrics=("survival","viable_teams","mean_net_food_per_living",
     "mean_gross_food_per_living","admin_per_living",
     "transfer_loss_per_living")
    row=dict(setting=name,environment=environment,governance=governance,
      parameters=parameters,
      **{key:float(np.mean([v[key] for v in by_seed])) for key in metrics},
      by_seed=by_seed)
    data.append(row)
   sample=next(x for x in data if x["setting"]==name and
     x["environment"]==environment and x["governance"]=="LOCAL_GLOBAL")
   none=next(x for x in data if x["setting"]==name and
     x["environment"]==environment and x["governance"]=="NONE")
   forecast=next(x for x in data if x["setting"]==name and
     x["environment"]==environment and x["governance"]=="FORECAST")
   print("V53B",name,environment,
     "NONE",round(none["survival"],4),
     "LOCAL_GLOBAL",round(sample["survival"],4),
     "FORECAST",round(forecast["survival"],4),
     "time",round(time.perf_counter()-start,1),flush=True)
 assert len(data)==len(VARIANTS)*len(ENVIRONMENT)*len(GOVERNANCE)==160
 output=dict(preregister="PREREG_V53B_SENSITIVITY.md",
  baseline_source="v53_vsm_material.py",
  original_v53_reference="v53_material_raw.json",
  worlds_per_seed=worlds,
  seeds=list(m.SEEDS),settings=list(VARIANTS),environments=list(ENVIRONMENT),
  governances=list(GOVERNANCE),
  total_worlds=len(data)*len(m.SEEDS)*worlds,
  rows=data,elapsed_seconds=time.perf_counter()-start)
 assert output["total_worlds"]==122880 if worlds==128 else True
 (ROOT/"results"/"v53b_sensitivity_raw.json").write_text(
  json.dumps(output,indent=1),encoding="utf8")
 print("V53B_FINISHED",len(data),"scenario-cells",
  output["total_worlds"],"worlds",flush=True)
 return output
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--worlds",type=int,default=128)
 a=p.parse_args()
 evaluate(a.worlds)
if __name__=="__main__":main()
