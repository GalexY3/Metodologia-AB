"""V34: EXACT V30 from-scratch privately learned contractual economy, degree 4.

Reuses V30 training code without editing rewards, policy, RNG seeds,
checkpoint format or optimizing objectives. Only changes graph degree.
"""
from __future__ import annotations
import argparse
from targeted_gifts import C as OriginalC
import v25_multi_capacity as base
import v30_consensual as contract

def run():
 p=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
 p.add_argument('--v34-degree',type=int,choices=(4,),required=True)
 arguments,_=p.parse_known_args()
 contract.install('mutual')
 previous_args=base.args
 def add_degree():
  parser=previous_args()
  parser.add_argument('--v34-degree',type=int,choices=(4,),required=True)
  return parser
 def degree_four(*args,**kwargs):
  assert kwargs.get('degree')==6
  kwargs['degree']=4
  return OriginalC(*args,**kwargs)
 base.args=add_degree
 base.C=degree_four
 base.main()
if __name__=='__main__':run()
