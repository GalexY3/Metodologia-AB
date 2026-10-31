"""N348 precommitted longitudinal comparison of full decentralized vs central ESBM.

Reference 60 central historical synthetic TS N341; 120 new actual 16-tick
decentralized runs. Verify first tick vs N347 fixed-decision shadow, then
track full dynamic paired differences by 6 seeds x 10 scenarios, no p-values.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'outcomes'/'N348_DECENTRALIZED_INDEX.json'
CENTRAL=ROOT/'outcomes'/'N341_TS60_INDEX.json'
SHADOW=ROOT/'outcomes'/'N347_CONDITIONAL_ALLOCATION_PROTOCOLS.json'
OUT=ROOT/'outcomes'/'N348_DYNAMIC_PROTOCOL_COMPARISON.json'
METRICS=['total_relationships_formed','total_dissolutions','active_partnerships_end',
         'total_impressions','total_proposals','total_positive_responses','mean_active_pairs']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise SystemExit('NO_OUTPUT_OVERWRITE')
    assert sha(CENTRAL)=='37b8a1010968e0ead1a13f7f71193858bcfb83b0e3428573ad734f96e136948d'
    assert sha(SHADOW)=='b1704a408d293d686cc4fb1a6b0d0645561b4dbd706e19c2244086539f6eb13a'
    assert sha(ROOT/'N341_INPUT_MANIFEST.json')=='84a52580add085ab551dacf6e4cd3fdfc80be8eeaf187c7d3e4b25be208e42bf'
    inputs=json.loads(SOURCE.read_text())['rows']
    expected=json.loads(CENTRAL.read_text())['rows']
    shadow=json.loads(SHADOW.read_text())['ticks']
    assert len(inputs)==120 and len(expected)==60 and len(shadow)==960
    table=[]
    for entry in inputs:
        seed,name,order=entry['seed'],entry['scenario'],entry['order']
        baseline=next(x for x in expected if x['seed']==seed and x['scenario']==name)
        r0=ROOT/'outcomes'/baseline['run_file'];r1=ROOT/'outcomes'/entry['run_file'];tr=ROOT/'outcomes'/entry['trace_file']
        assert sha(r0)==baseline['run_sha256'] and sha(r1)==entry['run_sha256'] and sha(tr)==entry['trace_sha256']
        central=json.loads(r0.read_text());alternative=json.loads(r1.read_text())
        if alternative['status']!='EXECUTED':
            table.append({'seed':seed,'scenario':name,'order':order,'status':alternative['status'],'error':alternative.get('error')})
            continue
        assert len(alternative['formation_pairs_by_tick'])==16 and len(alternative['tracks'])==16
        assert entry['matching_ticks']==16
        first_shadow=next(x for x in shadow if x['seed']==seed and x['scenario']==name and x['t']==0)
        label='chronological_first_accept' if order=='chronological' else 'reverse_chronological_first_accept'
        tick0_expected=first_shadow[label]['n_pairs']
        tick0_actual=len(alternative['formation_pairs_by_tick'][0])
        assert tick0_expected==tick0_actual,(seed,name,order,'FIRST_TICK_ABLATION_MISMATCH')
        diffs={k:alternative['result'][k]-central['result'][k] for k in METRICS}
        per_tick_pair_differences=sum(a!=b for a,b in zip(alternative['formation_pairs_by_tick'],central['formation_pairs_by_tick']))
        first_tick_different=alternative['formation_pairs_by_tick'][0]!=central['formation_pairs_by_tick'][0]
        table.append({'seed':seed,'scenario':name,'order':order,'status':'EXECUTED',
          'tick0_equals_N347_shadow_count':True,
          'central_tick0_pairs':len(central['formation_pairs_by_tick'][0]),
          'alt_tick0_pairs':tick0_actual,
          'first_tick_pair_identity_diff':first_tick_different,
          'ticks_with_different_pair_sets':per_tick_pair_differences,
          'central_metrics':{k:central['result'][k] for k in METRICS},
          'alternative_metrics':{k:alternative['result'][k] for k in METRICS},
          'paired_alternative_minus_central':diffs,
          'directed_events':entry['directed_events'],
          'trace_sha256':entry['trace_sha256'],
          'run_sha256':entry['run_sha256']})
    assert len(table)==120
    completed=[x for x in table if x['status']=='EXECUTED']
    by_order={}
    for order in ('chronological','reverse'):
        subset=[x for x in completed if x['order']==order]
        by_order[order]={
          'completed':len(subset),
          'ticks_with_different_matching_set':sum(x['ticks_with_different_pair_sets'] for x in subset),
          'first_ticks_with_different_matching_set':sum(x['first_tick_pair_identity_diff'] for x in subset),
          'central_total_formed':sum(x['central_metrics']['total_relationships_formed'] for x in subset),
          'alternative_total_formed':sum(x['alternative_metrics']['total_relationships_formed'] for x in subset),
          'central_final_active_partnerships_sum':sum(x['central_metrics']['active_partnerships_end'] for x in subset),
          'alternative_final_active_partnerships_sum':sum(x['alternative_metrics']['active_partnerships_end'] for x in subset),
          'paired_mean_difference_by_metric':{k:sum(x['paired_alternative_minus_central'][k] for x in subset)/len(subset) if subset else None for k in METRICS},
          'seed_level_total_formed_differences':{str(seed):sum(x['paired_alternative_minus_central']['total_relationships_formed'] for x in subset if x['seed']==seed) for seed in [101,211,307,401,503,601]}}
    # Prespecified negative control: first-tick cardinality must agree with
    # frozen N347 conditional shadow (same histories at t0); if not reject.
    report={'schema':'ABH_N348_FULL_DYNAMIC_DECENTRALIZED_VS_CENTRAL',
       'source_dynamic_index_sha':sha(SOURCE),
       'source_central_original_ts_index_sha':sha(CENTRAL),
       'source_N347_conditional_sha':sha(SHADOW),
       'rows':table,'complete_dynamic_runs':len(completed),
       'first_tick_shadow_controls_passed':sum(x.get('tick0_equals_N347_shadow_count',False) for x in completed),
       'orders':by_order,'comparison_not_human_causal':True,
       'identification_caveat':'These two full counterfactual worlds do recompute next-tick opportunities, choices and shocks under alternative partner states, but all agents obey simulator-provided accept/reject, exposure and hazard formulas; cannot transfer effect sizes to human romantic populations.',
       'no_p_values_without_external_human_cohort':True,
       'CT2_scientific':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N348_DYNAMIC_ORACLE',len(completed),'/120',
      'firsttick',report['first_tick_shadow_controls_passed'],
      'chron_formed',by_order['chronological']['alternative_total_formed'],
      'reverse_formed',by_order['reverse']['alternative_total_formed'],
      'SHA',sha(OUT))

if __name__=='__main__':main()
