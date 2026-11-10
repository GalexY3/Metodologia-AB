"""Posthoc exploratory negative control: untrained net, same seed and task.

The primary heldout was preregistered before inspecting outcomes. THIS
control is posthoc because it was added after seeing that greedy C2 differs
from stochastic C2. Never present this as confirmatory.
"""
import hashlib,json,torch,time
from pathlib import Path
from actors10 import IndependentActors10
from evaluate_v4 import run,ref_iid
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"untrained_greedy_control"
OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
LOCK={"analysis_type":"EXPLORATORY_ADDED_AFTER_V4_PRIMARY_RESULTS",
 "untrained_seed":421,"n":36,"hidden":64,"test_worldseed":"4900000+100*k",
 "actor_sha":sha(ROOT/"actors10.py"),
 "eval_sha":sha(ROOT/"evaluate_v4.py"),
 "control_script_sha":sha(ROOT/"test_untrained_greedy_v4.py"),
 "modes":["C1_greedy","C2_greedy"],"k":[2,3,4]}
p=OUT/"LOCK.json"
if p.exists():
 if json.loads(p.read_text(encoding="utf-8"))!=LOCK:raise RuntimeError("Lock changed")
else:p.write_text(json.dumps(LOCK,indent=2),encoding="utf-8")
torch.manual_seed(421)
actor=IndependentActors10(n=36,hidden=64)
actor.eval()
out=[]
for k in (2,3,4):
 floor=ref_iid(k)
 for mode in ("C1_greedy","C2_greedy"):
  dest=OUT/f"k{k}_{mode}.json"
  if dest.exists():raise RuntimeError("No overwrite")
  z=run(actor,k,mode,4900000+100*k,floor)
  dest.write_text(json.dumps(z,ensure_ascii=False,indent=2),encoding="utf-8")
  out.append({name:value for name,value in z.items() if name not in
    ("D_curve","churn_curve","occupied_curve","final_D_worlds",
     "final_occupied_worlds","exact_final_worlds")})
  print("UNTRAINED",k,mode,"D",round(z["D_final"],5),
        "occupied",round(z["occupied_final_mean"],3),
        "stable",z["stable_practical_count"],"exact",z["exact_count_final"],flush=True)
(OUT/"SUMMARY.json").write_text(json.dumps({"lock":LOCK,"cases":out,
 "status":"posthoc, exploratory only"},ensure_ascii=False,indent=2),encoding="utf-8")
