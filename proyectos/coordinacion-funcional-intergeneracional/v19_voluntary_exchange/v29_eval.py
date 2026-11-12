"""V29 frozen evaluations with exact trained observation and graph.

Delegates ALL benchmark and intervention logic to versioned V25 auditors.
Replaces only the previously registered V29 implementation differences:
own prior targeted recipients, degree 4 vs 6, and degree-4 oracle.
"""
from __future__ import annotations
import argparse,sys,json,torch
from pathlib import Path
import v25_multi_capacity as base
import v25_holdout as ho
import v25_causal_audit as causal
from targeted_gifts import C as OriginalC
from v29_train import PreciseGiftActor,precise_step
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
ROOT=Path(__file__).resolve().parent

@torch.no_grad()
def oracle_degree4(c,seed=401):
  if c.degree==6:
    return ORIGINAL_ORACLE(c,seed)
  assert c.k==4 and c.degree==4 and c.topology=="ring"
  w=start4(c,seed,"balanced")
  target=torch.arange(c.n,device=c.device)[None,:,None]
  offsets=torch.tensor([1,2,-1],device=c.device)[None,None,:]
  dests=((target+offsets)%c.n).expand(c.batch,-1,-1)
  gift=torch.ones(c.batch,c.n,3,device=c.device)
  food,_=base.step_multi(c,w,dests,gift)
  assert torch.all(w['full']==1)
  return dict(food=float(food.mean()),full=float(w["full"].mean()),
              cover=float(w["cover"].mean()),count=float(gift.sum(2).mean()))

ORIGINAL_ORACLE=ho.oracle
def main():
 p=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
 p.add_argument('--name',required=True)
 p.add_argument('--kind',choices=("holdout","causal"),required=True)
 opts,unknown=p.parse_known_args()
 # V25 delegates accept all other flags including --name.
 sys.argv=[sys.argv[0],"--name",opts.name]+unknown
 spec=json.loads((ROOT/"runs"/opts.name/"v25_spec.json").read_text("utf8"))
 assert spec["relational_feature"] in ("precise","legacy") and spec["degree"] in (4,6)
 degree=spec["degree"]
 def actual_C(*args,**kwargs):
    assert kwargs.get("degree",6)==6
    kwargs["degree"]=degree
    return OriginalC(*args,**kwargs)
 if spec["relational_feature"]=="precise":
    base.step_multi=precise_step
    ho.PrivateGiftActor=PreciseGiftActor
    causal.step_multi=precise_step
    # The frozen driver and all interventions must see the same corrected policy.
    assert ho.PrivateGiftActor is PreciseGiftActor
 else:
    assert base.step_multi is step_multi
 ho.C=actual_C
 causal.C=actual_C
 ho.oracle=oracle_degree4
 if opts.kind=="holdout":
    print("V29_AUDIT_CONFIG",opts.name,"holdout",spec["relational_feature"],degree,flush=True)
    ho.main()
 else:
    print("V29_AUDIT_CONFIG",opts.name,"causal",spec["relational_feature"],degree,flush=True)
    causal.main()
if __name__=="__main__":main()
