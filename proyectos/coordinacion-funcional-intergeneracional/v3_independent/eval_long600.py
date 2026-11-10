"""Prospective reserved evaluation of finished V3B 600-update models.

Frozen in PREREG_V3B_LONGRUN_HOLDOUT.md; no retraining and no tuning.
Same run_case from the existing 120-update evaluator, with fresh world seeds.
"""
from pathlib import Path
import json,hashlib,time
import torch
from individual_agents import IndependentActors
from evaluate_v3b import run_case
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"holdout_v3b_long"
OUT.mkdir(exist_ok=True)
torch.set_num_threads(2)
ks=(2,3,4)
conditions=("C1","C2","C3","random_always","random_T24","stay")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checkpoint(mode):
 return ROOT/"runs"/f"v3b_seed311_{mode}_updates600"/"FINAL_MODEL.pt"
lock={"protocol":"PREREG_V3B_LONGRUN_HOLDOUT.md",
 "models":{c:sha(checkpoint(c)) for c in ("C1","C2")},
 "eval_script":sha(ROOT/"eval_long600.py"),
 "existing_evaluator":sha(ROOT/"evaluate_v3b.py"),
 "policy":sha(ROOT/"individual_agents.py"),
 "env":sha(ROOT/"environment_v3.py"),
 "n":36,"k":list(ks),"worlds":100,"ticks":120,
 "world_seed":"2690000+100*k","model_train_seed":311}
lock_file=OUT/"LOCK.json"
if lock_file.exists():
 if json.loads(lock_file.read_text(encoding="utf-8"))!=lock:
  raise RuntimeError("Test code or models changed since freeze")
else:lock_file.write_text(json.dumps(lock,indent=2),encoding="utf-8")
agents={"training_seed":311}
for m in ("C1","C2"):
 ck=torch.load(checkpoint(m),map_location="cpu",weights_only=False)
 assert ck["update"]==600
 a=IndependentActors(n=36,hidden=ck["config"]["hidden"])
 a.load_state_dict(ck["model"]);a.eval()
 agents[m]=a
out=[]
t0=time.perf_counter()
for k in ks:
 for mode in conditions:
  file=OUT/f"k{k}_{mode}.json"
  if file.exists():raise RuntimeError("Refusing to overwrite reserved results")
  result=run_case(2690000+100*k,k,mode,agents)
  file.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
  out.append({a:b for a,b in result.items() if a not in
     ("final_world_D","stable_by_world","D_curve_mean","churn_curve_mean")})
  print("V3B_600_HOLDOUT",k,mode,"D",round(result["average_final_D"],5),
       "stable",result["stable_count"],"exact",result["exact_count"],
       "churn",round(result["average_last10_churn"],3),
       "elapsed",round(time.perf_counter()-t0,1),flush=True)
(OUT/"SUMMARY.json").write_text(json.dumps(
 {"lock":lock,"rows":out,
  "note":"One independent training cohort only, exploratory post hoc longer budget"},
 ensure_ascii=False,indent=2),encoding="utf-8")
print("V3B_600_HOLDOUT_FINISHED",round(time.perf_counter()-t0,1),flush=True)
