"""V45 clean initial-generosity intervention upon V44 independent RL.

Monkeypatch only the INITIAL Bernoulli bias and preserve the entire
V44 training code, parameters, optimizer, RNG seed and food equation.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import torch
import v44_private_dyads as base

def main():
 parser=argparse.ArgumentParser(add_help=False)
 parser.add_argument("--initial-bias",type=float,choices=(1.5,3.),required=True)
 a,other=parser.parse_known_args()
 old_argv=sys.argv[:]
 sys.argv=[old_argv[0]]+other
 orig=base.PrivateDyadic
 class BiasedActor(orig):
  def __init__(self,*args,**kwargs):
   super().__init__(*args,**kwargs)
   with torch.no_grad():self.bias.fill_(a.initial_bias)
 base.PrivateDyadic=BiasedActor
 try:
  base.main()
 finally:
  base.PrivateDyadic=orig
  sys.argv=old_argv
 # Write explicit metadata into completed spec only AFTER base runner returns.
 parsed=base.ROOT/"runs"
 original=argparse.ArgumentParser(add_help=False)
 original.add_argument("--name",required=True)
 opts,_=original.parse_known_args(other)
 folder=parsed/opts.name
 specpath=folder/"v44_spec.json"
 spec=json.loads(specpath.read_text("utf8"))
 spec["v45_initial_logit_bias"]=a.initial_bias
 spec["v45_initial_cooperation_probability"]=float(torch.sigmoid(torch.tensor(a.initial_bias)))
 spec["v45_exogenously_biased_initial_policy"]=True
 spec["v45_no_contracts_and_private_training"]=True
 specpath.write_text(json.dumps(spec,indent=2),encoding="utf8")
 (folder/"v45_status.json").write_text(json.dumps(dict(
  trained=True,original_model="v44_private_dyads.PrivateDyadic",
  only_difference="initial Bernoulli logit bias",
  initial_logit_bias=a.initial_bias,
  initial_cooperation_probability=spec["v45_initial_cooperation_probability"])),encoding="utf8")
 print("V45_BIASED_COMPLETE",opts.name,a.initial_bias,flush=True)
if __name__=="__main__":main()
