"""Prospectively frozen audit, exact enumeration and original-source helpers."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import numpy as np
import torch
from research_resource_limits import apply_limits
from v205_two_stage_game import sigmoid,aa_field,best_responses_p,trajectories
from v205_author_helpers import original_helper_probe

B=Path(__file__).resolve().parent


def main():
    reg=json.loads((B/'V205_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    assert reg['remote_bytes_verified_before_primary_audit']
    for name,digest in reg['source_sha256'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    out=B/'results/V205_ADVALIGN_NASH_AUDIT';out.mkdir(exist_ok=False)
    (out/'FREEZE.json').write_text(json.dumps(reg,indent=2),encoding='utf-8')
    theta=np.zeros((2,3));alpha=.1;rows=[];central=[]
    settings=[('joint',.95),('marginal',.95),('gae',0.),('gae',.95),('gae',1.)]
    for coupling,gamma,beta,variant,setting in itertools.product([0.,.1],[0.,.5,.9,.99],[0.,.1,.3,1.],['eq8','eq59'],settings):
        kind,lmbda=setting
        initial=best_responses_p(sigmoid(theta),gamma,coupling)
        field,own,extra=aa_field(theta,gamma,beta,variant,kind,lmbda,coupling)
        after=best_responses_p(sigmoid(theta+alpha*field),gamma,coupling)
        row=dict(coupling=coupling,gamma=gamma,beta=beta,variant=variant,advantages=kind,lmbda=lmbda,
            initial=initial,field=field.tolist(),own_field=own.tolist(),correction=extra.tolist(),after_step=after)
        if variant=='eq8' and kind=='joint':
            predicted=np.zeros((2,3));predicted[0,1:]=beta*gamma**3/4
            regret=gamma*(1+coupling)*math.tanh(alpha*beta*gamma**3/8)
            row.update(predicted_field=predicted.tolist(),maximum_field_error=float(np.max(np.abs(field-predicted))),
                predicted_player2_regret=regret,player2_regret_error=abs(after['gains'][1]-regret))
        rows.append(row)
        if gamma==.9 and beta==.3 and variant=='eq8' and kind=='joint':central.append(row)
    (out/'LITERAL_FIELDS.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    source=[]
    for coupling,mode,proximal,normalize,lmbda,dtype in itertools.product([0.,.1],['naive','integrated_aa','separated_aa'],
        [False,True],[False,True],[0.,.95,1.],['float64','float32']):
        source.append(original_helper_probe(coupling,mode,proximal,normalize,lmbda,dtype))
    (out/'AUTHOR_HELPERS.json').write_text(json.dumps(source,indent=2),encoding='utf-8')
    fixture=[]
    for coupling in [0.,.1]:
        for path in trajectories(sigmoid(theta),.9,coupling=coupling):
            fixture.append(dict(coupling=coupling,**{k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in path.items()}))
    (out/'FIXTURE.json').write_text(json.dumps(fixture,indent=2),encoding='utf-8')
    literal_ok=all(r['initial']['max_gain']<1e-12 and r['maximum_field_error']<1e-10 and
        r['after_step']['gains'][1]>1e-8 and r['player2_regret_error']<1e-10 for r in central)
    aa=[r for r in source if r['loss_mode']!='naive'];naive=[r for r in source if r['loss_mode']=='naive']
    source_ok=all(r['field_changes_player1_terminal'] and r['post_step_exploitable'] for r in aa)
    naive_ok=all(max(abs(x) for g in r['gradient'] for x in g)<(1e-10 if r['dtype']=='float64' else 1e-6) for r in naive)
    primary=dict(study='V205',status='AUDIT_COMPLETE',
        H1='CONFIRMED_INTERNAL_COUNTEREXAMPLE' if literal_ok and source_ok and naive_ok else 'NOT_CONFIRMED',
        literal_profiles=len(rows),author_helper_profiles=len(source),AA_source_profiles=len(aa),naive_source_controls=len(naive),
        literal_prediction_pass=literal_ok,source_helper_effect_pass=source_ok,naive_control_pass=naive_ok,
        central_cases=central,maximum_eq8_joint_field_error=max(r.get('maximum_field_error',0.) for r in rows),
        maximum_eq8_joint_regret_error=max(r.get('player2_regret_error',0.) for r in rows),
        implementations_are_internal_not_external_replication=True,
        independent_JS_audit_pending=True,original_priority_established=False,
        historical_CT2=61,new_branch_score=None,N2=0,N3=0,overall_goal='ACTIVE')
    (out/'SUMMARY.json').write_text(json.dumps(primary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in primary.items() if k!='central_cases'},indent=2))


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    main()
