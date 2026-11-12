"""V24b delayed-cost intervention (prespecified after V24-u200 failures).

Uses exactly V24's cold per-agent joint training, topology, reward, actors,
optimizer and reporting. Overrides ONLY the cost schedule.
"""
from pathlib import Path
import json,hashlib
import v24_k4_joint as base

def delayed_cost(a,update):
 assert a.schedule=="smooth" and a.updates>=a.transition+300
 assert a.low_cost<=a.cost
 if update==1:
  source=Path(base.__file__)
  params=dict(schedule="low-flat-then-linear-then-high",
      cost_low=a.low_cost,cost_high=a.cost,
      flat_through_update=a.transition,
      increase_through_update=a.transition+300,
      high_from_update=a.transition+300,
      updates=a.updates,
      base_script_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
      note="V24b custom schedule, NOT the V24 smooth schedule shown in common v24_spec.json. All model parameters initialized randomly.")
  p=base.ROOT/"runs"/a.name/"v24b_protocol.json"
  p.write_text(json.dumps(params,indent=2),encoding="utf8")
 if update<=a.transition:return a.low_cost
 fraction=min(1.,max(0.,(update-a.transition)/300.))
 return a.low_cost+(a.cost-a.low_cost)*fraction

base.cost_at=delayed_cost
if __name__=="__main__":base.main()
