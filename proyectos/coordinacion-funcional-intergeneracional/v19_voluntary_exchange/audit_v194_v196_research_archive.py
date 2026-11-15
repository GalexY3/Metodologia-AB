"""Reproducibility and archive-completeness checks for V194..V196.
Checks existence, recorded hashes, prespecified directions and source status.
Not independent scientific replication.
"""
import json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
R=ROOT/"results"
DIRS={"V194":R/"V194_PRIVATE_INFORMATION_LEARNING",
      "V195":R/"V195_CORRELATED_EXPLORATION",
      "V196":R/"V196_POST_PULSE_PLASTICITY"}
report=R/"INFORME_V194_V196_CREDIT_SCALING_AND_MAINTENANCE.md"
checks=[];records=[]
def verify(tag,condition,detail=""):
    checks.append(dict(check=tag,passed=bool(condition),detail=str(detail)))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
sources={"V194":ROOT/"v194_learned_information_institutions.py",
         "V195":ROOT/"v195_joint_signal_policy_exploration.py",
         "V196":ROOT/"v196_plastic_no_pulse_maintenance.py"}
pregs={"V194":ROOT/"PREREG_V194_PRIVATE_ENDOGENOUS_INFORMATION_VOTE.md",
         "V195":ROOT/"PREREG_V195_CORRELATED_PRIVATE_EXPLORATION.md",
         "V196":ROOT/"PREREG_V196_PLASTIC_MAINTENANCE_AFTER_EXPLORATION.md"}
wins=0;endogenic_75=0;pulse_superior=0;cases=0
for k in (4,8,12):
    for rule in ("UNANIMITY","MAJORITY"):
        cases+=1
        a=DIRS["V194"]/f"V194_k{k}_{rule}_W32_G20_T8000.json"
        aW=a.with_suffix(".npz")
        aAudit=DIRS["V194"]/f"V194A_exact_strategic_k{k}_{rule}.json"
        b=DIRS["V195"]/f"V195_k{k}_{rule}_W32_G20_T8000.json"
        bW=b.with_suffix(".npz")
        bAudit=DIRS["V195"]/f"V195A_FROZEN_NO_PULSE_AUDIT_k{k}_{rule}.json"
        c=DIRS["V196"]/f"V196_k{k}_{rule}_W32_G20_H8000.json"
        cW=c.with_suffix(".npz")
        for label,f in (("V194",a),("V194_weights",aW),("V194A",aAudit),
                        ("V195",b),("V195_weights",bW),("V195A",bAudit),
                        ("V196",c),("V196_weights",cW)):
            verify(f"{k}_{rule}_{label}_exists",f.exists(),str(f))
        j=json.loads(a.read_text("utf8"))
        y=json.loads(b.read_text("utf8"))
        z=json.loads(c.read_text("utf8"))
        aj=json.loads(aAudit.read_text("utf8"))
        by=json.loads(bAudit.read_text("utf8"))
        verify(f"{k}_{rule}_V194_source_SHA",j["source_sha256"]==sha(sources["V194"]))
        verify(f"{k}_{rule}_V195_source_SHA",y["source_sha256"]==sha(sources["V195"]))
        verify(f"{k}_{rule}_V196_source_SHA",z["method_sha"]==sha(sources["V196"]))
        verify(f"{k}_{rule}_V194_protocol",j["prereg_sha256"]==sha(pregs["V194"]))
        verify(f"{k}_{rule}_V195_protocol",y["prereg_sha256"]==sha(pregs["V195"]))
        verify(f"{k}_{rule}_V196_protocol",z["prereg_sha"]==sha(pregs["V196"]))
        verify(f"{k}_{rule}_V195A_binded_V195",by["experiment_sha256"]==sha(b))
        verify(f"{k}_{rule}_V196_binded_V195_weights",z["source_v195_sha"]==sha(bW))
        verify(f"{k}_{rule}_V196_exact_policies_match_prior",z["checks_exact_initial_matches_v195a"])
        yr={x["arm"]:x for x in y["rows"]}
        zr={x["arm"]:x for x in z["results"]}
        by_rows={x["arm"]:x for x in by["rows"]}
        verify(f"{k}_{rule}_training_pulse_intact",
          abs(by_rows["JOINT_SIGNAL_PULSE_10"]["pulse_train_empirical"]-.1)<.005)
        verify(f"{k}_{rule}_evaluation_has_no_pulse",
          all(x["phases"][-1]["world_pulse_mean"]==0. for x in y["rows"]))
        verify(f"{k}_{rule}_analytic_independent_observation_within_margin",
           all(x["monte_carlo_consistent_by_margin"] for x in by["rows"]))
        vr=zr["PLASTIC_NO_PULSE_EPS08"]["checkpoints"][-1]["mean_welfare"]
        prev=zr["FREEZE"]["checkpoints"][0]["mean_welfare"]
        vp=zr["PLASTIC_KEEP_PULSE_10"]["checkpoints"][-1]["mean_welfare"]
        exact=by_rows["JOINT_SIGNAL_PULSE_10"]["exact_welfare"]
        verify(f"{k}_{rule}_source_value_reproduced",abs(prev-exact)<1e-12)
        verify(f"{k}_{rule}_frozen_unchanged",
            all(abs(x["mean_welfare"]-prev)<1e-12 for x in zr["FREEZE"]["checkpoints"]))
        verify(f"{k}_{rule}_no_pulse_actually_zero",
            all(zr[a]["pulse_rate"]==0. for a in zr if a!="PLASTIC_KEEP_PULSE_10"))
        verify(f"{k}_{rule}_support_pulse_at_10_percent",
            abs(zr["PLASTIC_KEEP_PULSE_10"]["pulse_rate"]-.1)<.005)
        metric=y["comparisons"]["JOINT_SIGNAL_10_minus_IID_SIGNAL_PULSE_10"]
        if metric["world_paired_bootstrap95"][0]>0:wins+=1
        if vr>=.75*prev:endogenic_75+=1
        pp=z["comparisons"]["WITH_PULSE_minus_NO_PULSE_EPS08"]
        if pp["paired_ci95"][0]>0:pulse_superior+=1
        records.append(dict(k=k,rule=rule,benchmark_private=float(yr["STANDARD_PRIVATE"]["phases"][-1]["world_reward_mean"]),
            iid=float(yr["IID_SIGNAL_PULSE_10"]["phases"][-1]["world_reward_mean"]),
            joint=float(yr["JOINT_SIGNAL_PULSE_10"]["phases"][-1]["world_reward_mean"]),
            joint_minus_iid_ci95=metric["world_paired_bootstrap95"],
            initial_exact=prev,
            no_pulse_plastic_end=vr,retained_ratio_no_pulse=vr/prev,
            keep_pulse_plastic_end=vp,retained_ratio_keep_pulse=vp/prev,
            keep_minus_without_ci95=pp["paired_ci95"]))
verify("V195_joint_above_individual_CI_in_5_of_6",wins==5,wins)
verify("V196_75percent_retention_gate_failed_0of6",endogenic_75==0,endogenic_75)
verify("V196_pulse_maintain_positive_6of6",pulse_superior==6,pulse_superior)
verify("six_datasets_per_experiment",cases==6)
verify("report_exists",report.exists())
verify("fig1_exists",(R/"FIG_V195_COORDINATION_VS_INDEPENDENT_EXPLORATION.png").exists())
verify("fig2_exists",(R/"FIG_V196_COORDINATION_MAINTENANCE_K12_UNANIMITY.png").exists())
failed=[z for z in checks if not z["passed"]]
audit=dict(date="2026-11-15",status="PASS" if not failed else "FAIL",
  check_count=len(checks),failed=failed,experimental_scenarios=cases,
  V195_effect_positive_with_CI_count=wins,
  V196_autonomous_plastic_retention_ge_75pct_count=endogenic_75,
  V196_keep_pulse_significant_by_CI_count=pulse_superior,
  causal_interpretation="exogenously coordinated learning assists; not spontaneously created or self-maintaining institution",
  cannot_claim_N2=True,CT2=61,N2=0,N3=0,
  report_sha256=sha(report),rows=records,
  checks=checks)
out=R/"V194_V196_ARCHIVE_AUDIT_20261115.json"
assert not out.exists()
out.write_text(json.dumps(audit,indent=2),encoding="utf8")
print("V194_V196_AUDIT",audit["status"],len(checks),
       "failures",len(failed),
       "V195_significance",wins,
       "V196_retention",endogenic_75,"V196_pulse",pulse_superior)
if failed:print(json.dumps(failed,indent=2))
assert not failed
