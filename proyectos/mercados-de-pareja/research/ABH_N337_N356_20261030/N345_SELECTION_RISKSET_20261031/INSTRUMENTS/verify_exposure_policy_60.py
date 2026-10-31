"""N345 independent observable risk-set, Gumbel top-K, and visibility-policy oracle.

Reconstructs all 60 original ESBM 144x16 exposure sequences from frozen
population attributes, source RNG shocks, N342 true directed decisions, and
native matched pair/dissolution states. NEVER executes ESBM source or TS model.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/'outcomes'/'N345_INDEPENDENT_EXPOSURE_POLICY.json'
N=144;K=7;T=16

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def eligible_pair(p,i,j,mode):
    if i==j:return False
    gi,gj=p['genders'][i],p['genders'][j]
    if mode=='FM_only':return (gi=='F' and gj=='M') or (gi=='M' and gj=='F')
    def allows(a,b):
        x=p['scopes'][a]
        return x=='all' or (x=='same' and p['genders'][a]==p['genders'][b]) or (x=='other' and p['genders'][a]!=p['genders'][b])
    return allows(i,j) and allows(j,i)

def gumbel(u,mode,same,q,seen):
    v=min(1-1e-12,max(1e-12,float(u)))
    score=-math.log(-math.log(v))
    if mode=='same_norm':score+=1.7*int(same)
    elif mode=='popular':score+=3.5*(q-.5)
    elif mode=='balance':score-=1.4*math.log1p(seen)
    return score

def main():
    if OUTPUT.exists():raise SystemExit('NO_OVERWRITE')
    m=json.loads((ROOT/'N341_INPUT_MANIFEST.json').read_text())
    nidx=json.loads((ROOT/'outcomes'/'N342_NATIVE_INDEX.json').read_text())
    assert len(nidx['rows'])==60
    config={'mixed_random':('general','random'),
      'heterosexual_restricted':('FM_only','random'),
      'institutional_segregation':('general','same_norm'),
      'explicit_norm_preference':('general','random'),
      'popularity_ranking':('general','popular'),
      'visibility_balancing':('general','balance'),
      'private_rejection_learning':('general','random'),
      'public_rejection_signal':('general','random'),
      'longer_partnerships':('general','random'),
      'shorter_partnerships':('general','random')}
    assert list(config)==m['scenario_order']
    cases=[];sample_mutant=None
    for seedrow in m['rows']:
        seed=seedrow['seed'];f=ROOT/'official_inputs_60'/seedrow['people']['path']
        assert sha(f)==seedrow['people']['sha256']
        p=json.loads(f.read_text(encoding='utf8'))
        filename=ROOT/'official_inputs_60'/seedrow['tensors']['u_expose']['path']
        assert sha(filename)==seedrow['tensors']['u_expose']['sha256']
        shocks=np.memmap(filename,dtype='<f8',mode='r',shape=(T,N,N))
        for name in config:
            mode,policy=config[name]
            native=next(z for z in nidx['rows'] if z['seed']==seed and z['scenario']==name)
            trace=ROOT/'outcomes'/native['trace_path'];runs=ROOT/'outcomes'/native['run_path']
            assert sha(trace)==native['trace_sha256'] and sha(runs)==native['run_sha256']
            sr=json.loads(runs.read_text(encoding='utf8'))
            tick_events=[[] for _ in range(T)]
            with trace.open(encoding='utf8') as fd:
                for line in fd:
                    e=json.loads(line)
                    tick_events[e['t']].append(e)
            partner=[-1]*N;seen=[0]*N
            checked=0
            # primary outcomes: first mismatch is retained but not 'repaired'
            first_difference=None;cutoff_gaps=[];risks=[];total_exposures=0;same_exposures=0
            for t in range(T):
                records=tick_events[t]
                breaks=[e for e in records if e['stage']=='dissolution']
                existing=[(i,j) for i,j in enumerate(partner) if j>i]
                observed=[(e['i'],e['j']) for e in breaks]
                if observed!=existing and first_difference is None:
                    first_difference={'t':t,'stage':'dissolution','expected':existing,'observed':observed}
                for e in breaks:
                    i,j=e['i'],e['j']
                    if e['decision']:
                        partner[i]=partner[j]=-1
                available=[i for i in range(N) if partner[i]<0]
                risk=sum(eligible_pair(p,i,j,mode) for k,i in enumerate(available) for j in available[k+1:])
                risks.append(risk)
                if sr['result']['track'][t]['risk_edges']!=risk and first_difference is None:
                    first_difference={'t':t,'stage':'risk_set','expected':risk,'observed':sr['result']['track'][t]['risk_edges']}
                exposed=[e for e in records if e['stage']=='exposure']
                exp_by_sender={i:[] for i in available}
                for e in exposed:
                    if e['i'] not in exp_by_sender:
                        if first_difference is None:first_difference={'t':t,'stage':'ineligible_sender','event':e}
                    else:exp_by_sender[e['i']].append(e['j'])
                for i in available:
                    candidates=[j for j in available if eligible_pair(p,i,j,mode)]
                    if not candidates:
                        if exp_by_sender[i] and first_difference is None:
                            first_difference={'t':t,'sender':i,'error':'EXPOSURE_WITHOUT_CANDIDATE'}
                        continue
                    scored=[(gumbel(shocks[t,i,j],policy,p['norm'][i]==p['norm'][j],p['q'][j],seen[j]),j) for j in candidates]
                    sorted_scores=sorted(scored)
                    kk=min(K,len(candidates))
                    target=[j for _,j in sorted_scores[-kk:]]
                    actual=exp_by_sender[i]
                    if target!=actual and first_difference is None:
                        first_difference={'t':t,'sender':i,'stage':'selection','expected':target,'observed':actual,'policy':policy}
                    checked+=1
                    if len(candidates)>kk:
                        cutoff_gaps.append(sorted_scores[-kk][0]-sorted_scores[-kk-1][0])
                        if sample_mutant is None and kk>=2:
                            excluded=sorted_scores[-kk-1][1]
                            mutated_scores=sorted((score+1e9 if j==excluded else score,j) for score,j in scored)
                            mutant_selected=[j for _,j in mutated_scores[-kk:]]
                            assert mutant_selected!=target and excluded in mutant_selected
                            sample_mutant={'seed':seed,'scenario':name,'t':t,'sender':i,
                              'selected':target,'excluded_candidate':excluded,
                              'mutated_topk':mutant_selected,
                              'mutant_test':'Artificially boosted excluded candidate score +1e9 and confirmed top-k changes, not native observation'}
                    for j in actual:
                        seen[j]+=1;total_exposures+=1;same_exposures+=int(p['norm'][i]==p['norm'][j])
                pairs=sr['formation_pairs_by_tick'][t]
                for a,b in pairs:
                    if (partner[a]>=0 or partner[b]>=0 or not eligible_pair(p,a,b,mode)) and first_difference is None:
                        first_difference={'t':t,'stage':'invalid_formation','pair':[a,b]}
                    partner[a]=b;partner[b]=a
                if len(exposed)!=sr['result']['track'][t]['impressions'] and first_difference is None:
                    first_difference={'t':t,'stage':'exposure_count','expected':len(exposed),'observed':sr['result']['track'][t]['impressions']}
            if total_exposures!=sr['result']['total_impressions'] and first_difference is None:
                first_difference={'stage':'total_exposure','expected':total_exposures,'observed':sr['result']['total_impressions']}
            group_ratio=same_exposures/total_exposures if total_exposures else None
            if group_ratio is not None and abs(group_ratio-sr['result']['group_same_exposure'])>1e-12 and first_difference is None:
                first_difference={'stage':'same_norm_exposure','expected':group_ratio,'observed':sr['result']['group_same_exposure']}
            gender={g:sum(seen[i] for i in range(N) if p['genders'][i]==g) for g in ['F','M','X']}
            if gender!=sr['result']['impression_count_by_gender'] and first_difference is None:
                first_difference={'stage':'gender_exposure_count','expected':gender,'observed':sr['result']['impression_count_by_gender']}
            cases.append({'seed':seed,'scenario':name,'policy':policy,'status':'EXACT' if first_difference is None else 'MISMATCH',
              'first_difference':first_difference,'actor_riskset_selections_checked':checked,
              'exposures_checked':total_exposures,'same_norm_exposure_fraction':group_ratio,
              'minimum_gumbel_selection_cutoff_gap':min(cutoff_gaps) if cutoff_gaps else None,
              'ties_at_cutoff':sum(x==0 for x in cutoff_gaps),
              'cutoffs_within_1e_minus_12':sum(x<=1e-12 for x in cutoff_gaps),
              'risk_edges_sum':sum(risks)})
    assert sample_mutant
    sample=sample_mutant
    # Independent selection tamper control validates exclusion is a real risk-set counterexample.
    assert sample['excluded_candidate'] not in sample['selected']
    result={'schema':'N345_INDEPENDENT_RISKSET_GUMBEL_POLICY_ORACLE',
      'original_Python_index_SHA':sha(ROOT/'outcomes'/'N342_NATIVE_INDEX.json'),
      'frozen_original_shocks_SHA':sha(ROOT/'N341_INPUT_MANIFEST.json'),
      'cases':cases,'runs_checked':len(cases),
      'policy_and_opportunity_exact_runs':sum(x['status']=='EXACT' for x in cases),
      'actor_level_selection_risksets_checked':sum(x['actor_riskset_selections_checked'] for x in cases),
      'individual_exposures_checked':sum(x['exposures_checked'] for x in cases),
      'cutoffs_with_near_ties':sum(x['cutoffs_within_1e_minus_12'] for x in cases),
      'negative_control_excluded_candidate_mutant':sample,
      'synthetic_only':True,'human_data_rows':0,'CT2_scientific':7,'STOP_R5_human':True}
    OUTPUT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N345_POLICY_ORACLE',result['policy_and_opportunity_exact_runs'],'/60',
      'actor_risksets',result['actor_level_selection_risksets_checked'],
      'exposures',result['individual_exposures_checked'],
      'near_cutoff_ties',result['cutoffs_with_near_ties'],'SHA',sha(OUTPUT))

if __name__=='__main__':main()
