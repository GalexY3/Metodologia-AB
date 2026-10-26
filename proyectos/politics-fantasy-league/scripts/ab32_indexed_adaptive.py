#!/usr/bin/env python3
"""C26-C32: adaptive historical-group drift localization with documented institutional dates.

Date POOL comes from institutional search/calendar dates. A date is not a
cycle assignment until the preceding cycle is observed and the next is
preregistered. Genuine source URLs and SHA fingerprints are required.
All fields are aggregates; no person values or scoring.
"""
from pathlib import Path
from datetime import date,datetime,timezone
from collections import defaultdict
import json
from ab32_adaptive_survey import audit,norm
P=Path("/tmp/pf-congress-probe")
OUTPUT=P/"adaptive_indexed_c26_c32.json"
TRACE=P/"adaptive_indexed_trace.jsonl"
# Source-indexed, *candidate pool*, not a calendar of cycle assignments.
DATES=["2024-09-10","2024-11-12","2024-12-10","2024-12-12",
"2025-03-25","2025-05-06","2025-06-12","2025-09-10",
"2025-11-27","2025-12-11","2026-09-22"]
PUBLISHER_INDEX_SOURCES=["https://www.congreso.es/es/cem/sepdic2024",
"https://www.congreso.es/es/cem/sepdic2025",
"https://www.congreso.es/es/opendata/votaciones?targetDate=09%2F04%2F2024&targetLegislatura=XV",
"https://www.congreso.es/es/opendata/votaciones?targetDate=11%2F12%2F2025&targetLegislatura=XV"]
TARGET=date(2024,12,10)

def next_day(previous,attempted,verified):
   avail=[date.fromisoformat(d) for d in DATES if date.fromisoformat(d) not in attempted]
   if not avail:return None,"NO_INDEXED_DAY"
   if previous is None:return TARGET,"FIRST_TEST_AFTER_C25_GROUP_ANOMALY"
   prior=date.fromisoformat(previous["date"])
   if previous["status"]!="ORIGINAL_RETRIEVED":
       return min(avail,key=lambda d:(abs((d-prior).days),d)),"SOURCE_LINK_FAILURE_NEIGHBOR_INDEXED_DAY"
   if previous["group_map_conflicts"] or previous["unmatched_person_strings"]:
       # FOCUS: move forward at least one month to locate disappearance.
       ahead=[d for d in avail if d>prior and (d-prior).days>=28]
       if ahead:return min(ahead),"LOCATE_ANOMALY_FORWARD_IN_HISTORY"
       return max(avail),"ANOMALY_LATE_BOUNDS"
   # BRANCH: choose time away from validated earlier samples, reduce overfit.
   anchors=[date(2024,4,9),date(2026,7,23),date(2026,9,10),date(2026,9,30)]+verified
   return max(avail,key=lambda d:(min(abs((d-a).days) for a in anchors),d)),"TEMPORAL_COVERAGE_GENERALIZATION"

def main():
    active=json.loads((P/"official_1.json").read_text())
    departed=json.loads((P/"official_7.json").read_text())
    roster={norm(v["NOMBRE"]):v for v in active+departed}
    first=json.loads((P/"vote_original.json").read_text())
    group=defaultdict(set)
    for v in first["votaciones"]:
        x=roster.get(norm(v["diputado"]))
        if x:group[v["grupo"]].add(x["GRUPOPARLAMENTARIO"])
    priors={"verified_original_indexed_dates":{"alpha":2,"beta":6},
       "conditional_2026_roster_group_transfer":{"alpha":1,"beta":3}}
    done=[];attempted=set();passed=[];prev=None;fail=0
    for i in range(26,33):
        day,why=next_day(prev,attempted,passed)
        if day is None:break
        mode="GROUP_DRIFT_LOCALIZATION" if (prev is None or prev.get("group_map_conflicts") or prev.get("unmatched_person_strings")) else ("SOURCE_AVAILABILITY" if prev.get("status")!="ORIGINAL_RETRIEVED" else "LONGITUDINAL_GENERALIZATION")
        question={
          "GROUP_DRIFT_LOCALIZATION":"Do source-scoped group/name anomalies persist at the next selected indexed historical session?",
          "SOURCE_AVAILABILITY":"Can an adjacent officially indexed sitting repair previous source-access failure?",
          "LONGITUDINAL_GENERALIZATION":"Does the same 2026 roster correspondence hold at a temporally distant originally published sitting?"
        }[mode]
        record={"id":"C"+str(i),"A_question":question,
            "B_hypotheses":{"H1":"original exists, metadata and chronology auditable","H0":"official source fails or historical group/person mismatch persists"},
            "C_prior":json.loads(json.dumps(priors)),
            "D_method":"official Congress page href→authentic JSON SHA→source-scoped group, name, period and rollcall arithmetic",
            "E_prereg_at":datetime.now(timezone.utc).isoformat(),
            "E_target_day":str(day),"E_decision_after_preceding":why,
            "F_result":None,"G_adversarial":"selection is active and dependent, no inferential representativeness; group codes not party IDs; no first_public_at",
            "H_closure":None,"I_posterior":None,"J_next_strategy":None}
        with TRACE.open("a",encoding="utf8") as h:
            h.write(json.dumps({"event":"PRE_OBSERVATION", "id":record["id"],"date":str(day),"chosen_after":why,"priors":priors},ensure_ascii=False)+"\n");h.flush()
        attempted.add(day)
        try:
            observation=audit(day,group,roster)
        except Exception as exc:
            observation={"status":"STOP_R5","error_type":type(exc).__name__,"error_code":str(exc)[:80],"scoreable_people":0}
        record["F_result"]=observation
        success=observation["status"]=="ORIGINAL_RETRIEVED" and observation["source_vote_tally_matches"]
        priors["verified_original_indexed_dates"]["alpha" if success else "beta"]+=1
        no_mismatch=success and not (observation["unmatched_person_strings"] or observation["group_map_conflicts"] or observation["invalid_office_intervals"] or observation["duplicate_vote_name_strings"])
        if success:
            priors["conditional_2026_roster_group_transfer"]["alpha" if no_mismatch else "beta"]+=1
            passed.append(day)
        record["H_closure"]="BOUNDED_NO_MISMATCH" if no_mismatch else ("BOUNDED_HISTORIC_ANOMALY" if success else "STOP_R5_SOURCE_ABSENT")
        record["I_posterior"]=json.loads(json.dumps(priors))
        record["J_next_strategy"]="LOCALIZE_ANOMALY" if success and not no_mismatch else ("INDEXED_SOURCE_PIVOT" if not success else "DIVERSIFY_TIME")
        record["observed_at"]=datetime.now(timezone.utc).isoformat()
        print("AB32_INDEXED_CYCLE="+json.dumps(record,ensure_ascii=False),flush=True)
        done.append(record)
        with TRACE.open("a",encoding="utf8") as h:
            h.write(json.dumps({"event":"EVIDENCE_UPDATE_THEN_NEXT_SELECTION", "id":record["id"],"closure":record["H_closure"],"posterior":priors},ensure_ascii=False)+"\n")
        OUTPUT.write_text(json.dumps({"policy":"INDEXED_SOURCE_SEQUENTIAL_V1", "records":done,"priors":priors,"unexecuted_count":7-len(done),"publisher_index_sources":PUBLISHER_INDEX_SOURCES},ensure_ascii=False,indent=2)+"\n")
        prev={"date":str(day),**observation}
        fail=0 if success else fail+1
        if fail>=3:
            print("AB32_INDEXED_STOP=THREE_CONSECUTIVE_FAILURES")
            break
    print("AB32_INDEXED_SUMMARY="+json.dumps({"executed":len(done),"actual_originals":sum(x["F_result"]["status"]=="ORIGINAL_RETRIEVED" for x in done),"bounded_clean":sum(x["H_closure"]=="BOUNDED_NO_MISMATCH" for x in done),"bounded_anomaly":sum(x["H_closure"]=="BOUNDED_HISTORIC_ANOMALY" for x in done),"R5":sum(x["H_closure"]=="STOP_R5_SOURCE_ABSENT" for x in done),"unexecuted":7-len(done),"priors":priors}))
if __name__=="__main__":main()
