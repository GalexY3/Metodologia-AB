"""V26: exact V25 protocol with only longer individual donor memory.

Uses the original V25 implementation without edits; replaces the C factory
in the loaded V25 module to pass through private memory_decay, which changes
only the trust update already implemented in v25_multi_capacity.step_multi.
"""
from __future__ import annotations
import argparse
from targeted_gifts import C
import v25_multi_capacity as base

def run():
 peek=argparse.ArgumentParser(add_help=False)
 peek.add_argument("--memory-decay",type=float,required=True)
 parsed,_=peek.parse_known_args()
 delta=parsed.memory_decay
 assert 0<=delta<1 and delta in (0.,.94,.99),delta
 oldargs=base.args
 def addmemory():
  p=oldargs()
  p.add_argument("--memory-decay",type=float,required=True)
  return p
 def memoryfactory(*args,**kwargs):
  kwargs["memory_decay"]=delta
  return C(*args,**kwargs)
 base.args=addmemory
 base.C=memoryfactory
 base.main()
if __name__=="__main__":run()
