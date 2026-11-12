"""V26 frozen heldout under the trained individual-memory decay.

Reuses original V25 frozen evaluator; makes only the C(memory_decay)
constructor match what V26 had during training. Does not modify V25.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from targeted_gifts import C as OriginalC
import v25_holdout as original
ROOT=Path(__file__).resolve().parent
def configure():
 p=argparse.ArgumentParser(add_help=False)
 p.add_argument("--name",required=True)
 args,_=p.parse_known_args()
 spec=json.loads((ROOT/"runs"/args.name/"v25_spec.json").read_text("utf8"))
 delta=spec.get("memory_decay")
 assert delta in (.94,.99),delta
 def cwithmemory(*args,**kwargs):
  kwargs["memory_decay"]=delta
  return OriginalC(*args,**kwargs)
 original.C=cwithmemory
 return delta
if __name__=="__main__":
 print("V26_MEMORY_EVAL",configure(),flush=True)
 original.main()
