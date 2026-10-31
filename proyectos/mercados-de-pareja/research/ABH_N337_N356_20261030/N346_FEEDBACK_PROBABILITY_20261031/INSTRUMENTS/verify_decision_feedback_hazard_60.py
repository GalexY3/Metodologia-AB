"""N346 mathematically independent ESBM event-state probability & shock oracle.

Reconstructs the original 60 traces from immutable native outcomes, original
shocks and attributes, with a fresh state machine for private rejection bias,
public reputation and dissolution hazard. Does NOT execute either ESBM engine.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outcomes'/'N346_DECISION_FEEDBACK_HAZARD_ORACLE.json'
SCALE=1e-12
SCENARIOS=['mixed_random','heterosexual_restricted','institutional_segregation',
  'explicit_norm_preference','popularity_ranking','visibility_balancing',
  'private_rejection_learning','public_rejection_signal',
  'longer_partnerships','shorter_partnerships']
CONF={name:dict(same_pref=1.3 if name=='explicit_norm_preference' else 0,
                private=name=='private_rejection_learning',
                public=name=='public_rejection_signal',
                hazard_mult=.4 if name=='longer_partnerships' else 1.75 if name=='shorter_partnerships' else 1)
      for name in SCENARIOS}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def logistic(x):return 1/(1+math.exp(-max(-25,min(25,float(x)))))

def main():
    if OUT.exists():raise SystemExit('NO_OUTPUT_OVERWRITE')
    manifest=ROOT/'N341_INPUT_MANIFEST.json';assert sha(manifest)=='84a52580add085ab551dacf6e4cd3fdfc80be8eeaf187c7d3e4b25be208e42bf'
    native=ROOT/'outcomes'/'N342_NATIVE_INDEX.json';assert sha(native)=='89e221ab34c1a3c08ff04c8902268946f1b40cf6230cea224a907d9e96bd776b'
    events=json.loads(native.read_text())['rows']
    seeds=json.loads(manifest.read_text())['rows']
    cases=[];adversarial_bias_and_reputation=[]
    for seedrow in seeds:
        seed=seedrow['seed']
        people_path=ROOT/'official_inputs_60'/seedrow['people']['path']
        assert sha(people_path)==seedrow['people']['sha256']
        p=json.loads(people_path.read_text(encoding='utf8'))
        shock={}
        for kind in ['u_send','u_reply','u_hazard','u_expose']:
            rec=seedrow['tensors'][kind]
            path=ROOT/'official_inputs_60'/rec['path']
            assert sha(path)==rec['sha256']
            shock[kind]=np.memmap(path,dtype='<f8',mode='r',shape=(16,144,144))
        for name in SCENARIOS:
            r=next(x for x in events if x['seed']==seed and x['scenario']==name)
            trace=ROOT/'outcomes'/r['trace_path'];results=ROOT/'outcomes'/r['run_path']
            assert sha(trace)==r['trace_sha256'] and sha(results)==r['run_sha256']
            native_run=json.loads(results.read_text())['result']
            config=CONF[name]
            bias=[0.0]*144;reputation=[0.0]*144
            counts={kind:0 for kind in ['exposure','proposal','response','dissolution']}
            rejected=0;decision_margins=[];diffs=0;first=None
            actual_decision_mismatches=0
            for line in trace.open(encoding='utf8'):
                e=json.loads(line)
                kind=e['stage'];i=e['i'];j=e['j'];t=e['t']
                counts[kind]+=1
                same=int(p['norm'][i]==p['norm'][j]);gap=abs(p['age'][i]-p['age'][j]);
                expected_p=None
                if kind=='exposure':
                    expected_u=float(shock['u_expose'][t,i,j]);provided=e['u_expose']
                elif kind=='dissolution':
                    expected_u=float(shock['u_hazard'][t,i,j]);provided=e['u']
                    expected_p=min(.90,(.12+.065*(1-same)+.004*gap)*config['hazard_mult'])
                elif kind=='proposal':
                    expected_u=float(shock['u_send'][t,i,j]);provided=e['u']
                    utility=-.85+1.6*(p['q'][j]-.5)+config['same_pref']*same-.012*gap+bias[i]
                    expected_p=logistic(utility)
                elif kind=='response':
                    expected_u=float(shock['u_reply'][t,j,i]);provided=e['u']
                    utility=-.85+1.6*(p['q'][i]-.5)+config['same_pref']*same-.012*gap+(reputation[i] if config['public'] else 0)
                    expected_p=logistic(utility)
                else:raise AssertionError('UNEXPECTED_EVENT_STAGE')
                if not (math.isfinite(expected_u) and expected_u==provided) and first is None:
                    first={'stage':'SHOCK', 'event_index':sum(counts.values()),'event':e,'expected':expected_u}
                    diffs+=1
                if expected_p is not None:
                    if not math.isfinite(e['p']) or abs(expected_p-e['p'])>SCALE:
                        diffs+=1
                        if first is None:first={'stage':'PROBABILITY','event_index':sum(counts.values()),'event':e,'expected':expected_p}
                    decision_margins.append(abs(expected_u-expected_p))
                    predicted=bool(expected_u<expected_p)
                    if predicted!=e['decision']:
                        actual_decision_mismatches+=1
                        if first is None:first={'stage':'DECISION','event_index':sum(counts.values()),'event':e,'expected':predicted}
                if kind=='response' and not e['decision']:
                    rejected+=1
                    if config['private']:
                        before=bias[i]
                        bias[i]=min(.80,bias[i]+.08)
                        if before!=bias[i] and len(adversarial_bias_and_reputation)<8:
                            default_p=logistic(-.85+1.6*(p['q'][j]-.5)-.012*gap+before)
                            perturbed_p=logistic(-.85+1.6*(p['q'][j]-.5)-.012*gap+bias[i])
                            assert perturbed_p>default_p
                            adversarial_bias_and_reputation.append({'seed':seed,'scenario':name,'channel':'private','effect':'INCREASE_FUTURE_SEND_PROBABILITY','p_before':default_p,'p_after':perturbed_p})
                    if config['public']:
                        before=reputation[i]
                        reputation[i]=max(-1.8,reputation[i]-.08)
                        if before!=reputation[i] and len(adversarial_bias_and_reputation)<16:
                            default_p=logistic(-.85+1.6*(p['q'][i]-.5)-.012*gap+before)
                            perturbed_p=logistic(-.85+1.6*(p['q'][i]-.5)-.012*gap+reputation[i])
                            assert perturbed_p<default_p
                            adversarial_bias_and_reputation.append({'seed':seed,'scenario':name,'channel':'public','effect':'DECREASE_FUTURE_REPLY_PROBABILITY','p_before':default_p,'p_after':perturbed_p})
            biasavg=sum(bias)/len(bias);repavg=sum(reputation)/len(reputation)
            if abs(biasavg-native_run['final_private_aspiration_bias_mean'])>1e-12 and first is None:
                first={'stage':'FINAL_PRIVATE_BIAS','expected':biasavg,'observed':native_run['final_private_aspiration_bias_mean']}
            if abs(repavg-native_run['final_public_reputation_penalty_mean'])>1e-12 and first is None:
                first={'stage':'FINAL_PUBLIC_SCORE','expected':repavg,'observed':native_run['final_public_reputation_penalty_mean']}
            if counts['exposure']!=native_run['total_impressions'] and first is None:
                first={'stage':'EXPOSURE_COUNT','expected':counts['exposure'],'observed':native_run['total_impressions']}
            if counts['proposal']!=native_run['total_impressions'] and first is None:
                first={'stage':'PROPOSAL_TRIAL_COUNT','expected':counts['proposal'],'observed':native_run['total_impressions']}
            numpropose=sum(1 for line in (ROOT/'outcomes'/r['trace_path']).open(encoding='utf8') if '"stage":"proposal"' in line and '"decision":true' in line)
            if numpropose!=native_run['total_proposals'] and first is None:
                first={'stage':'POSITIVE_PROPOSAL_COUNT','expected':numpropose,'observed':native_run['total_proposals']}
            cases.append({'seed':seed,'scenario':name,'status':'EXACT' if first is None else 'NEGATIVE',
              'first_difference':first,'event_counts':counts,'rejections':rejected,
              'probability_or_shock_errors':diffs,'decision_errors':actual_decision_mismatches,
              'min_decision_shock_probability_margin':min(decision_margins) if decision_margins else None,
              'decisions_with_margin_le_1e_minus_12':sum(x<=1e-12 for x in decision_margins),
              'decisions_with_margin_le_1e_minus_9':sum(x<=1e-9 for x in decision_margins),
              'decisions_with_margin_le_1e_minus_6':sum(x<=1e-6 for x in decision_margins),
              'final_private_bias_mean':biasavg,'final_public_score_mean':repavg})
    assert any(x['channel']=='private' for x in adversarial_bias_and_reputation)
    assert any(x['channel']=='public' for x in adversarial_bias_and_reputation)
    report={'schema':'N346_INDEPENDENT_PROBABILITIES_FEEDBACK_HAZARD',
       'original_Python_index_sha':sha(native),
       'original_input_manifest_sha':sha(manifest),
       'cases':cases,'exact_runs':sum(x['status']=='EXACT' for x in cases),
       'directed_events_checked':sum(sum(x['event_counts'].values()) for x in cases),
       'decision_events_checked':sum(x['event_counts']['proposal']+x['event_counts']['response']+x['event_counts']['dissolution'] for x in cases),
       'margin_below_1e_minus_12':sum(x['decisions_with_margin_le_1e_minus_12'] for x in cases),
       'margin_below_1e_minus_9':sum(x['decisions_with_margin_le_1e_minus_9'] for x in cases),
       'margin_below_1e_minus_6':sum(x['decisions_with_margin_le_1e_minus_6'] for x in cases),
       'min_shock_probability_margin':min(x['min_decision_shock_probability_margin'] for x in cases),
       'adversarial_feedback_direction_controls':adversarial_bias_and_reputation,
       'scientific_limits':'Original ESBM uses rejection to increase private proposal propensity and decrease public reply propensity; independent arithmetic check of stipulated rules, NOT evidence real daters react this way.',
       'CT2':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N346_STATE_ORACLE',report['exact_runs'],'/60',
      'directed',report['directed_events_checked'],
      'thresholds_le_1e-12',report['margin_below_1e_minus_12'],
      'minimum_margin',report['min_shock_probability_margin'],
      'SHA',sha(OUT))

if __name__=='__main__':main()
