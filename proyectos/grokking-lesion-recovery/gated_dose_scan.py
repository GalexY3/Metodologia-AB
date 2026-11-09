"""Pilot damage-dose selection to avoid calling zero damage 'fast recovery'.
No recovery training, no checkpoint selection by lesion outcome.
"""
import argparse,json,statistics,csv
from pathlib import Path
import numpy as np
import torch
from gated_v6 import GatedNet,build_data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
@torch.no_grad()
def test():
 p=argparse.ArgumentParser();p.add_argument("--checkpoints",nargs="+",required=True)
 p.add_argument("--masks",type=int,default=25);a=p.parse_args()
 records=[]
 for ck in a.checkpoints:
  blob=torch.load(ck,map_location="cpu",weights_only=False);c=blob["config"]
  net=GatedNet(c["p"],c["dim"],c["branch_hidden"]);net.load_state_dict(blob["model"])
  x,y,idx=build_data(c["p"],c["noise_total"],c["train_frac"],c["valid_frac"],c["split_seed"])
  sel=idx["val"];z=net(x[sel]);base=float((z.argmax(1)==y[sel]).float().mean())
  for k in [15,30,45,60,90]:
   for maskseed in range(100,100+a.masks):
    rng=np.random.default_rng(maskseed)
    picks=rng.choice(150,size=k,replace=False)
    net.clean.mask[:] = 1
    net.clean.mask[picks]=0
    z=net(x[sel])
    val=float((z.argmax(1)==y[sel]).float().mean())
    records.append({"model":Path(ck).parent.name,"k_clean":k,"mask_seed":maskseed,"base":base,"injured":val,"damage_pp":100*(base-val)})
   subset=[r for r in records if r["model"]==Path(ck).parent.name and r["k_clean"]==k]
   print("DOSE",Path(ck).parent.name,"k",k,"base",round(base,3),
      "mean_pp",round(statistics.mean(r["damage_pp"] for r in subset),2),
      "max_pp",round(max(r["damage_pp"] for r in subset),2),
      "over5pp",sum(r["damage_pp"]>5 for r in subset),"/",len(subset),flush=True)
 path=ROOT/"gated_dose_scan.csv"
 with path.open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
if __name__=="__main__":test()
