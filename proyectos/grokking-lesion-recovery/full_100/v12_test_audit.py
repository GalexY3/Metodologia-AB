"""Run one reserved-test audit only AFTER V12_GATES.json & V12_ROBUSTNESS.json
were finalized. Do not use test outcomes to edit eligibility or schedules.
"""
from pathlib import Path
import json,hashlib
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data

torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
gates_path=ROOT/"V12_GATES.json"
robust_path=ROOT/"V12_ROBUSTNESS.json"
if not gates_path.is_file() or not robust_path.is_file():
 raise RuntimeError("Cannot open test until eligibility and validation lesion analysis frozen.")
gates=json.loads(gates_path.read_text(encoding="utf-8"))
robust=json.loads(robust_path.read_text(encoding="utf-8"))
assert not robust["test_evaluated"]
assert gates["test_not_consulted"]
seeds=gates["eligible_for_lesions"]
assert seeds==robust["eligible_seeds"]
x,y,ids=data(20261110,500,1000,2000)
ix=ids["test"]
xt=x[ix];yt=y[ix]
# Check no repeated cases across train/val/test
uniq=set(tuple(row) for row in x.int().tolist())
assert len(uniq)==len(x),"data duplicate across splits"
@torch.no_grad()
def test_result(seed,lam,step):
 path=ROOT/"v12_runs"/f"seed{seed}_prior{lam:g}"/f"ck_{step:06d}.pt"
 ck=torch.load(path,map_location="cpu",weights_only=False)
 m=MLP(300);m.load_state_dict(ck["model"])
 m.eval();z=m(xt)
 return {"seed":seed,"prior_lambda":lam,"step":step,
  "test_acc":float((z.argmax(1)==yt).float().mean()),
  "test_ce":float(F.cross_entropy(z,yt)),
  "n_test":len(yt)}
rows=[test_result(seed,lam,step) for seed in seeds for lam in (1e-5,.001) for step in (6000,10000)]
out={"status":"One-time secondary audit, test sealed from choice of arms/masks and validation analysis",
 "gate_file_sha256":hashlib.sha256(gates_path.read_bytes()).hexdigest(),
 "validation_file_sha256":hashlib.sha256(robust_path.read_bytes()).hexdigest(),
 "eligible_seeds":seeds,"test_partition_seed":20261110,"results":rows,
 "all_test100":all(r["test_acc"]==1 for r in rows)}
(ROOT/"V12_TEST_AUDIT.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("TEST_AUDIT",json.dumps({"n":len(rows),"all_test100":out["all_test100"],
 "min_test_acc":min([r["test_acc"] for r in rows],default=None),
 "not_perfect":[r for r in rows if r["test_acc"]<1]},ensure_ascii=False),flush=True)
