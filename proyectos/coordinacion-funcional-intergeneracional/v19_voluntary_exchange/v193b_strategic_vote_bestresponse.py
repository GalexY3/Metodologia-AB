"""V193B independent vote best-response and exhaustive probability audit.
Signal-following is not assumed optimal. This is a falsification gate.
"""
from __future__ import annotations
from itertools import product
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
PREG=ROOT/"PREREG_V193B_STRATEGIC_VOTE_AUDIT.md"
OUT=ROOT/"results/V193B_EXACT_STRATEGIC_VOTE_AUDIT.json"
PI=Q(3,5);A=Q(4,5);GOOD=Q(1,1)
KS=(4,8,12,24);LOSSES=(1,3,5,8);RULES=("UNANIMITY","MAJORITY")
MODES=("INDEPENDENT","PUBLIC")
def sigprob(q,s):
    return q if s=="POSITIVE" else 1-q
def direct(m,h,L,mode,signal):
    # Enumerates private other-signal profiles with rational probability
    # independent of the closed-form binomial pivotal identity.
    val=Q()
    for isgood in (False,True):
        theta_weight=PI if isgood else 1-PI
        q=A if isgood else 1-A
        sprob=sigprob(q,signal)
        reward=GOOD if isgood else -Q(L)
        if mode=="PUBLIC":
            votes=[1]* (m-1) if signal=="POSITIVE" else [0]*(m-1)
            yes=int(sum(votes)+1>=h)
            no=int(sum(votes)>=h)
            val+=theta_weight*sprob*reward*(yes-no)
        else:
            for votes in product((0,1),repeat=m-1):
                p=Q(1)
                for vote in votes:p*=q if vote else 1-q
                yes=int(sum(votes)+1>=h);no=int(sum(votes)>=h)
                val+=theta_weight*sprob*p*reward*(yes-no)
    return val

def closed(m,h,L,mode,signal):
    plus=signal=="POSITIVE"
    if mode=="INDEPENDENT":
        def pivotal(q):
            return Q(comb(m-1,h-1))*q**(h-1)*(1-q)**(m-h)
        pg=pivotal(A);pb=pivotal(1-A)
    else:
        pg=pb=Q(1) if ((plus and h==m) or ((not plus) and h==1)) else Q()
    return PI*sigprob(A,signal)*pg*GOOD-(1-PI)*sigprob(1-A,signal)*pb*L

def make():
    assert not OUT.exists()
    rows=[];fail=[];n_direct=0
    for k,rule,L,mode in product(KS,RULES,LOSSES,MODES):
        m=k-1;h=m if rule=="UNANIMITY" else m//2+1
        vals={}
        for sig in ("POSITIVE","NEGATIVE"):
            z=closed(m,h,L,mode,sig)
            vals[sig]=z
            if k<=12:
                oracle=direct(m,h,L,mode,sig)
                n_direct+=1
                if z!=oracle:fail.append(dict(k=k,rule=rule,L=L,mode=mode,signal=sig,
                                           closed=str(z),direct=str(oracle)))
        # Positive vote is current action on positive signal, so deviation no is
        # profitable if its acceptance marginal is strictly negative.
        # Negative vote is current action after negative signal; deviation yes
        # is profitable if acceptance marginal is strictly positive.
        unstable_pos=vals["POSITIVE"]<0
        unstable_neg=vals["NEGATIVE"]>0
        rows.append(dict(k=k,m=m,L=L,rule=rule,mode=mode,
            delta_yes_minus_no_positive=float(vals["POSITIVE"]),
            delta_yes_minus_no_negative=float(vals["NEGATIVE"]),
            delta_positive_exact=f"{vals['POSITIVE'].numerator}/{vals['POSITIVE'].denominator}",
            delta_negative_exact=f"{vals['NEGATIVE'].numerator}/{vals['NEGATIVE'].denominator}",
            following_positive_best_response=not unstable_pos,
            following_negative_best_response=not unstable_neg,
            signal_follow_profile_nash=not unstable_pos and not unstable_neg,
            violation_signals=["POSITIVE" if unstable_pos else None,"NEGATIVE" if unstable_neg else None]))
    d={(z["k"],z["rule"],z["L"],z["mode"]):z for z in rows}
    gates={
        "ind_unanimity_k4_L8_best_response":d[4,"UNANIMITY",8,"INDEPENDENT"]["signal_follow_profile_nash"],
        "ind_unanimity_k8_L8_negative_deviation":d[8,"UNANIMITY",8,"INDEPENDENT"]["delta_yes_minus_no_negative"]>0,
        "ind_unanimity_k4_L3_negative_deviation":d[4,"UNANIMITY",3,"INDEPENDENT"]["delta_yes_minus_no_negative"]>0,
        "pub_unanimity_k4_L8_positive_veto":d[4,"UNANIMITY",8,"PUBLIC"]["delta_yes_minus_no_positive"]<0,
        "ind_majority_k4_L3_best_response":d[4,"MAJORITY",3,"INDEPENDENT"]["signal_follow_profile_nash"],
        "ind_majority_k4_L8_positive_veto":d[4,"MAJORITY",8,"INDEPENDENT"]["delta_yes_minus_no_positive"]<0,
        "pub_majority_k4_all_nonpivotal": all(d[4,"MAJORITY",L,"PUBLIC"]["delta_yes_minus_no_positive"]==0 and
             d[4,"MAJORITY",L,"PUBLIC"]["delta_yes_minus_no_negative"]==0 for L in LOSSES)}
    assert all(gates.values()),gates
    assert not fail,fail
    vals={}
    for k in KS:
        m=k-1
        vals[str(k)]=dict(
            threshold_L_negative_follow_unanimity=float(PI/(1-PI)*(A/(1-A))**(m-2)),
            threshold_L_positive_follow_unanimity=float(PI/(1-PI)*(A/(1-A))**m))
    res=dict(date="2026-11-15", status="PASS", n_rows=len(rows), exact_direct_enumeration_tests=n_direct,
        exact_direct_misses=fail, preregistered_gates=gates,
        theory_roles_follow_signals_exogenously=True,
        economic_conclusion="Many signal-following policies from V193 are NOT private Nash best responses",
        prior_art="Voting with public info and correlated signals classical; no novelty claimed",
        thresholds=vals, rows=rows, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        prereg_sha256=hashlib.sha256(PREG.read_bytes()).hexdigest(),CT2_unchanged=61,N2=0,N3=0)
    OUT.write_text(json.dumps(res,indent=2),encoding="utf8")
    print("V193B_COMPLETE",json.dumps(dict(rows=len(rows),direct_parities=n_direct,
       failures=len(fail),gates=gates,thresholds=vals)),flush=True)
if __name__=="__main__":make()
