"""Audit structural integrity of the V7 pilot (not an external replication)."""
from pathlib import Path
import hashlib,json,csv,math,datetime
ROOT=Path(__file__).resolve().parent
result=json.loads((ROOT/"V7_ANALYSIS.json").read_text(encoding="utf-8"))
n=0;failed=[];mask_pairs=0
for seed in (0,1,2):
 for mask in range(101,106):
  pairs=[]
  for wd in (1.0,2.5):
   label=f"cleanWD{wd}_noiseWD0.05_init1.0_s{seed}_train0.55"
   d=ROOT/"gated_lesions"/f"{label}_ck_022000_c60_n0_mask{mask}"
   path=d/"summary.json"
   if not path.is_file():failed.append(f"missing {path}");continue
   obj=json.loads(path.read_text(encoding="utf-8"))
   if obj["n_clean"]!=60 or obj["n_noise"]!=0 or len(set(obj["masked_clean"]))!=60 or obj["masked_noise"]!=[]:failed.append(f"cardinality {path}")
   if obj["repair_optimizer"]!={"type":"AdamW fresh","lr":.001,"wd":.1}:failed.append(f"optimizer {path}")
   with (d/"metrics.csv").open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
   arms={a:[r for r in rows if r["arm"]==a] for a in ("no_lesion","lesion")}
   for arm,vals in arms.items():
    steps=[int(r["step"]) for r in vals]
    if steps!=list(range(0,651,10)):failed.append(f"step_grid {d} {arm}")
    for r in vals:
     if not (math.isfinite(float(r["val_acc"])) and math.isfinite(float(r["clean_val_acc"]))):failed.append(f"nonfinite {d}")
   if abs(float(arms["no_lesion"][0]["val_acc"])-obj["baseline_validation"])>1e-7:failed.append(f"baseline {d}")
   pairs.append(obj["masked_clean"])
   n+=1
  if len(pairs)==2:
   mask_pairs+=1
   if pairs[0]!=pairs[1]:failed.append(f"unmatched masks seed{seed} mask{mask}")
files=("gated_v6.py","gated_lesion_v6.py","v7_report.py","gated_dose_scan.py","v7_mechanism_probe.py")
sha={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
prereg=ROOT/"PILOT_V7_PREREG.md"
status={"status":"PASS" if n==30 and mask_pairs==15 and not failed else "FAIL",
       "lesion_runs":n,"paired_masks":mask_pairs,"failed_checks":failed,
       "code_sha256":sha,"preregister_file_exists":prereg.is_file(),
       "model_pair_eligibility":[x["eligible"] for x in result["gates"]],
       "scientific_status":"exploratory with no true non-grokking control; NOT independent audit"}
(ROOT/"V7_INTEGRITY_AUDIT.json").write_text(json.dumps(status,indent=2),encoding="utf-8")
print(json.dumps(status,indent=2))
