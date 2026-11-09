"""Descriptive grouped recovery times, no inferential claim."""
import json,statistics as st
from pathlib import Path
p=Path(__file__).resolve().parent
datasets=[
("V12B",json.loads((p/"V12B_RAW.json").read_text(encoding="utf-8"))["results"],"prior_lambda","initial_val_damage_pp","recovery_step_two_consecutive",500),
("V11C",json.loads((p/"V11C_RAW.json").read_text(encoding="utf-8"))["results"],"initial_lambda","initial_damage_val_pp","recovery_val99_two_consecutive_step",500),
("V10B",json.loads((p/"V10_LESION_RAW.json").read_text(encoding="utf-8"))["observations"],"lambda","initial_damage_val_pp","recovery_two_consecutive_val99_step",400)]
for label,rows,group,damage,reco,h in datasets:
 for dose in sorted(set(z.get("dose",90) for z in rows)):
  for lam in (1e-5,.001):
   sel=[z for z in rows if z[group]==lam and z.get("dose",90)==dose and z[damage]>2]
   times=[z[reco] for z in sel]
   observed=[x for x in times if x is not None]
   print(label,"dose",dose,"lambda",lam,"n_damage",len(sel),"n_recovered",len(observed),
      "median_event_step",st.median(observed) if observed else None,
      "restricted_mean_to_horizon",round(st.mean([x if x is not None else h+10 for x in times]),2) if times else None)
