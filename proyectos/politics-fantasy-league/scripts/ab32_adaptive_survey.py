#!/usr/bin/env python3
"""C19-C32 conditional sequential source-study; 14 is a CEILING, not a quota.

Each candidate/date/question is picked only after observing the immediately
preceding result. Before a new network request, a preregistration snapshot
is flushed to disk. Numeric Beta trackers are sampling diagnostics, not
credibility of parliamentary performance and not population inference.
No personal names are ever printed, persisted, or attributed to scoring.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date,datetime,timedelta,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse,urljoin,quote
import hashlib,json,re,unicodedata
ROOT=Path("/tmp/pf-congress-probe")
ROOT.mkdir(parents=True,exist_ok=True)
POLICY="C19_C32_ADAPTIVE_VALIDITY_V1"
ALL=ROOT/"adaptive_c19_c32.json"
LOG=ROOT/"adaptive_trace.jsonl"
VALID_MONTHS={2,3,4,5,6,9,10,11}
START=date(2024,2,1)
END=date(2026,9,30)
ANCHORS=(date(2026,7,23),date(2026,9,10),date(2026,9,30))
MAX_CYCLES=14

class Links(HTMLParser):
    def __init__(self):super().__init__();self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            u=dict(attrs).get("href")
            if u:self.hrefs.append(u)

def norm(s):
    return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())

def dated(s):
    if not re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}",str(s)):raise ValueError("UNEXPECTED_DATE")
    a,b,c=(int(v) for v in s.split("/"))
    return date(c,b,a)

def https_source(url,cap=4_000_000):
    with urlopen(Request(url,headers={"User-Agent":"PFL-AB32-Research/0.1"}),timeout=9) as response:
        loc=urlparse(response.geturl())
        if loc.scheme!="https" or loc.hostname!="www.congreso.es" or response.status!=200:
            raise ValueError("UNTRUSTED_CONGRESS_SOURCE")
        raw=response.read(cap+1)
    if len(raw)>cap or len(raw)<100:raise ValueError("SOURCE_SIZE_OUT_OF_LIMIT")
    return raw

def approved_dates():
    candidates=[]
    cursor=START
    while cursor<=END:
        if cursor.month in VALID_MONTHS and cursor.weekday() in (2,3):
            if cursor not in ANCHORS:candidates.append(cursor)
        cursor+=timedelta(days=1)
    return candidates

def select_day(mode,previous,attempted,passed):
    # Date selection has no fixed per-cycle itinerary. Anomaly branches
    # investigate adjacent weeks; source failures try preceding weekday once.
    pool=[d for d in approved_dates() if d not in attempted]
    if not pool:return None,"CANDIDATE_EXHAUSTED"
    if previous and mode=="SOURCE_ACCESS_BRANCH" and previous["requested_date"]:
        prior=date.fromisoformat(previous["requested_date"])
        near=[d for d in pool if 0<abs((d-prior).days)<=2]
        if near and previous.get("branch_retry",0)==0:
            return min(near,key=lambda d:abs((d-prior).days)),"ADJACENT_DATE_SOURCE_DIAGNOSTIC"
    if previous and mode in ("LOCALIZE_GROUP_MAP","LOCALIZE_NAME_OR_TERM"):
        prior=date.fromisoformat(previous["requested_date"])
        neighbors=[d for d in pool if 6<=abs((d-prior).days)<=21]
        if neighbors:
            return min(neighbors,key=lambda d:(abs((d-prior).days),d)),"NEIGHBOR_SESSION_ANOMALY_LOCALIZATION"
    distant=[d for d in pool if all(abs((d-t).days)>12 for t in attempted)]
    if distant:pool=distant
    refs=ANCHORS+tuple(passed)
    # Maximum temporal distance from previously verified dates, with
    # Thursday preference; fixed policy but actual target depends on results.
    best=max(pool,key=lambda d:(min(abs((d-t).days) for t in refs),d.weekday()==3,d))
    return best,"MAXIMIZE_HISTORICAL_TIME_SEPARATION"

def branch_from(outcome):
    if outcome.get("status")!="ORIGINAL_RETRIEVED":
        return "SOURCE_ACCESS_BRANCH"
    if outcome.get("group_map_conflicts",0):
        return "LOCALIZE_GROUP_MAP"
    if outcome.get("unmatched_person_strings",0) or outcome.get("invalid_office_intervals",0):
        return "LOCALIZE_NAME_OR_TERM"
    return "TEMPORAL_TRANSFER"

def audit(day,group_alias,roster):
    fmt=day.strftime("%d/%m/%Y")
    query="https://www.congreso.es/es/opendata/votaciones?targetDate="+quote(fmt,safe="")+"&targetLegislatura=XV"
    page=https_source(query,3_000_000)
    doc=Links();doc.feed(page.decode("utf-8","replace"))
    stamp=day.strftime("%Y%m%d")
    urls=[]
    for href in doc.hrefs:
        target=urljoin(query,href)
        p=urlparse(target)
        if (p.scheme=="https" and p.hostname=="www.congreso.es" and
            re.fullmatch(r"/webpublica/opendata/votaciones/Leg15/Sesion\d+/"+stamp+r"/Votacion\d+/VOT_\d+\.json",p.path)):
            urls.append(target)
    urls=sorted(set(urls))
    if not urls:raise ValueError("OFFICIAL_DATE_HAS_NO_MATCHING_VOTES")
    raw=https_source(urls[0],4_000_000)
    v=json.loads(raw)
    info=v["informacion"]
    if dated(info["fecha"])!=day:raise ValueError("DOCUMENT_DATE_NOT_TARGET")
    source_session=int(re.search(r"/Sesion(\d+)/",urlparse(urls[0]).path).group(1))
    if info["sesion"]!=source_session:raise ValueError("SESSION_MISMATCH")
    rows=v["votaciones"]
    if not isinstance(rows,list) or not rows:raise ValueError("EMPTY_VOTE_ROWS")
    tally=Counter(row["voto"] for row in rows)
    totals=v["totales"]
    matched=(tally["Sí"],tally["No"],tally["Abstención"],tally["No vota"])==(totals["afavor"],totals["enContra"],totals["abstenciones"],totals["noVotan"])
    unknown=0;role_bad=0;group_bad=0;duplicates=0;seen=set()
    for row in rows:
        name=norm(row["diputado"])
        if name in seen:duplicates+=1
        seen.add(name)
        member=roster.get(name)
        if member is None:
            unknown+=1;continue
        start=dated(member["FECHAALTA"])
        end=dated(member["FECHABAJA"]) if member.get("FECHABAJA") else None
        if day<start or (end is not None and day>=end):role_bad+=1
        if member["GRUPOPARLAMENTARIO"] not in group_alias.get(row["grupo"],set()):
            group_bad+=1
    return {
        "status":"ORIGINAL_RETRIEVED","source_url":urls[0],
        "source_sha256":hashlib.sha256(raw).hexdigest(),"session":source_session,
        "vote_number":info["numeroVotacion"],"original_date":str(day),
        "date_scoped_official_urls":len(urls),"vote_rows":len(rows),
        "source_vote_tally_matches":matched,
        "source_yes":tally["Sí"],"source_no":tally["No"],
        "source_abstain":tally["Abstención"],"source_no_vote":tally["No vota"],
        "unmatched_person_strings":unknown,"invalid_office_intervals":role_bad,
        "group_map_conflicts":group_bad,"duplicate_vote_name_strings":duplicates,
        "source_read_only":True,"scoreable_people":0
    }

def main():
    a=json.loads((ROOT/"official_1.json").read_text(encoding="utf-8-sig"))
    b=json.loads((ROOT/"official_7.json").read_text(encoding="utf-8-sig"))
    reg={norm(z["NOMBRE"]):z for z in a+b}
    orig=json.loads((ROOT/"vote_original.json").read_text())
    aliases=defaultdict(set)
    for v in orig["votaciones"]:
        member=reg.get(norm(v["diputado"]))
        if member:aliases[v["grupo"]].add(member["GRUPOPARLAMENTARIO"])
    priors={"date_source_capture":{"alpha":1,"beta":1},"conditional_name_group_temporal_transfer":{"alpha":1,"beta":1}}
    attempted=set();verified=[];prev=None;mode="TEMPORAL_TRANSFER";failure_streak=0
    results=[]
    for ordinal in range(19,33):
        day,reason=select_day(mode,prev,attempted,verified)
        if day is None:break
        question={
            "TEMPORAL_TRANSFER":"Does independently selected Congress historical date reproduce exact roster/role/group correspondence?",
            "SOURCE_ACCESS_BRANCH":"Is prior missing-date source problem local to date, with valid alternative in nearby weekday?",
            "LOCALIZE_GROUP_MAP":"Did source group nomenclature shift near the observed conflicting session?",
            "LOCALIZE_NAME_OR_TERM":"Is person-string or term-interval anomaly localized temporally to a neighboring session?"
        }[mode]
        cycle={"id":"C"+str(ordinal),"A_question":question,
            "B_alternatives":["H1 authentic date-matched source and coherent aggregates","H0 missing source or group/name/term anomaly"],
            "C_policy":"conditional source-day selection and original SHA",
            "D_instrument":"verified HTTPS Congress HTML source href and original JSON; no personal values exported",
            "E_prereg_created_before_download":datetime.now(timezone.utc).isoformat(),
            "E_source_date_selected":str(day),"E_selection_reason":reason,
            "E_prior_before":json.loads(json.dumps(priors)),
            "F_observation":None,"G_adversarial":"Selection adaptive and correlated; Beta engineering heuristic not population estimate; no immutable person IDs/rights/first-public.",
            "H_decision":None,"I_priors_after":None,"J_next_condition":None}
        # Force a durable pre-observation write before accessing source.
        with LOG.open("a",encoding="utf8") as out:
            out.write(json.dumps({"event":"PREREG_BEFORE_NETWORK", "id":cycle["id"],"date":str(day),"question":question,"prior":priors},ensure_ascii=False)+"\n")
            out.flush()
        attempted.add(day)
        try:
            obs=audit(day,aliases,reg)
        except Exception as err:
            obs={"status":"STOP_R5","error_type":type(err).__name__,"error_code":str(err)[:70],"original_verified":False,"scoreable_people":0}
        cycle["F_observation"]=obs
        ok=obs["status"]=="ORIGINAL_RETRIEVED" and obs.get("source_vote_tally_matches") is True
        priors["date_source_capture"]["alpha" if ok else "beta"]+=1
        transferable=ok and not obs["unmatched_person_strings"] and not obs["invalid_office_intervals"] and not obs["group_map_conflicts"] and not obs["duplicate_vote_name_strings"]
        if ok:
            priors["conditional_name_group_temporal_transfer"]["alpha" if transferable else "beta"]+=1
            verified.append(day)
        failure_streak=0 if ok else failure_streak+1
        cycle["H_decision"]="ACCEPT_SOURCE_BOUNDED" if transferable else ("ACCEPT_SOURCE_FLAG_ANOMALY" if ok else "STOP_R5_SOURCE_NOT_AVAILABLE")
        cycle["I_priors_after"]=json.loads(json.dumps(priors))
        mode=branch_from(obs)
        prev={"requested_date":str(day),**obs,"branch_retry":(0 if ok else (prev.get("branch_retry",0)+1 if prev and prev.get("status")!="ORIGINAL_RETRIEVED" else 0))}
        cycle["J_next_condition"]=mode
        cycle["observed_at"]=datetime.now(timezone.utc).isoformat()
        results.append(cycle)
        print("AB32_ADAPTIVE_RECORD="+json.dumps(cycle,ensure_ascii=False),flush=True)
        with LOG.open("a",encoding="utf8") as out:
            out.write(json.dumps({"event":"OBSERVATION_AND_PRIOR_UPDATE", "id":cycle["id"],"result":cycle["H_decision"],"posterior":priors,"next_mode":mode},ensure_ascii=False)+"\n")
        ALL.write_text(json.dumps({"policy":POLICY,"cycle_limit":MAX_CYCLES,"cycles":results,"priors":priors,"unexecuted_cycles":list(range(ordinal+1,33))},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        if failure_streak>=5:
            print("AB32_ADAPTIVE_EARLY_STOP=FIVE_CONSECUTIVE_OFFICIAL_SOURCE_FAILURES")
            break
    print("AB32_ADAPTIVE_SUMMARY="+json.dumps({"executed":len(results),"accepted":sum(x["H_decision"]=="ACCEPT_SOURCE_BOUNDED" for x in results),"real_originals":sum(x["F_observation"]["status"]=="ORIGINAL_RETRIEVED" for x in results),"stop_r5":sum(x["H_decision"]=="STOP_R5_SOURCE_NOT_AVAILABLE" for x in results),"posteriors":priors,"max_remaining":14-len(results)},ensure_ascii=False))
if __name__=="__main__":main()
