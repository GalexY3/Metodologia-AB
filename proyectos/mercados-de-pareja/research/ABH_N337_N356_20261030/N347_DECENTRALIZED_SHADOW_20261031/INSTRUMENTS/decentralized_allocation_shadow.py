"""N347 pre-frozen conditional allocation protocol shadow experiment.

Uses 960 genuine historical ESBM original positive directed decisions as fixed
opportunity/acceptance sets. Contrasts centralized exact max-cardinality/weight
matching with chronological and reverse chronological immediate pair formation.

Counterfactual ONLY conditional on the observed native decisions: after choosing
different pairs, actual later exposure/choices would change and are NOT replayed.
"""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outcomes'/'N347_CONDITIONAL_ALLOCATION_PROTOCOLS.json'
NAMES=['mixed_random','heterosexual_restricted','institutional_segregation',
  'explicit_norm_preference','popularity_ranking','visibility_balancing',
  'private_rejection_learning','public_rejection_signal',
  'longer_partnerships','shorter_partnerships']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sequential(responses):
    occupied=set();pairs=[]
    for i,j in responses:
        if not (0<=i<144 and 0<=j<144 and i!=j):
            raise ValueError('INVALID_MUTUAL_RESPONSE_EDGE')
        if i not in occupied and j not in occupied:
            occupied.add(i);occupied.add(j)
            pairs.append(tuple(sorted((i,j))))
    return sorted(pairs)

def main():
    if OUT.exists():raise SystemExit('NO_OVERWRITE')
    nidx=ROOT/'outcomes'/'N342_NATIVE_INDEX.json';tsidx=ROOT/'outcomes'/'N341_TS60_INDEX.json'
    inpath=ROOT/'N341_INPUT_MANIFEST.json'
    assert sha(nidx)=='89e221ab34c1a3c08ff04c8902268946f1b40cf6230cea224a907d9e96bd776b'
    assert sha(tsidx)=='37b8a1010968e0ead1a13f7f71193858bcfb83b0e3428573ad734f96e136948d'
    assert sha(inpath)=='84a52580add085ab551dacf6e4cd3fdfc80be8eeaf187c7d3e4b25be208e42bf'
    src=json.loads(nidx.read_text())['rows'];input=json.loads(inpath.read_text())['rows']
    assert len(src)==60
    ticks=[];shocks_by_seed={}
    for seedrow in input:
        seed=seedrow['seed'];f=seedrow['tensors']['u_match']
        p=ROOT/'official_inputs_60'/f['path'];assert sha(p)==f['sha256']
        shocks_by_seed[seed]=np.memmap(p,dtype='<f8',mode='r',shape=(16,144,144))
    for r in src:
        seed,name=r['seed'],r['scenario']
        assert name in NAMES and seed in shocks_by_seed
        results=ROOT/'outcomes'/r['run_path'];trace=ROOT/'outcomes'/r['trace_path']
        assert sha(results)==r['run_sha256'] and sha(trace)==r['trace_sha256']
        official=json.loads(results.read_text())
        accepted=[[] for _ in range(16)]
        with trace.open(encoding='utf8') as fd:
            for line in fd:
                e=json.loads(line)
                if e['stage']=='response' and e['decision']:
                    accepted[e['t']].append((e['i'],e['j']))
        for t in range(16):
            current=accepted[t]
            central=[tuple(p) for p in official['formation_pairs_by_tick'][t]]
            chron=sequential(current)
            reverse=sequential(list(reversed(current)))
            graph={tuple(sorted(x)) for x in current}
            assert len(graph)>=len(central)
            assert all(x in graph for x in central)
            assert len(set(v for e in central for v in e))==2*len(central)
            assert len(chron)<=len(central) and len(reverse)<=len(central)
            def residue(pairs):
                tensor=shocks_by_seed[seed]
                return sum(int((float(1+1e-4*float(tensor[t,a,b]))-1)*2**52) for a,b in pairs)
            centralres=residue(central)
            def row(pairs):
                overlap=len(set(pairs)&set(central))
                return {'n_pairs':len(pairs),'lost_pairs_vs_central':len(central)-len(pairs),
                  'identical_pair_set':set(pairs)==set(central),
                  'pair_overlap_count':overlap,
                  'pair_overlap_jaccard':overlap/len(set(pairs)|set(central)) if (pairs or central) else 1.,
                  'exact_integer_residue':residue(pairs)}
            ticks.append({'seed':seed,'scenario':name,'t':t,'eligible_mutual_undirected_edges':len(graph),
              'positive_directional_responses':len(current),
              'central_optimal_pairs':len(central),
              'central_exact_residue':centralres,
              'chronological_first_accept':row(chron),
              'reverse_chronological_first_accept':row(reverse),
              'reverse_vs_forward_pair_sets_identical':chron==reverse})
    assert len(ticks)==960
    # Adversarial negative: a self-edge cannot be silently accepted.
    try:
        sequential([(17,17)])
    except ValueError as e:
        assert str(e)=='INVALID_MUTUAL_RESPONSE_EDGE'
    else:raise AssertionError('MUTANT_SELF_EDGE_NOT_DETECTED')
    case_records=[]
    for seed in [101,211,307,401,503,601]:
        for name in NAMES:
            cohort=[x for x in ticks if x['seed']==seed and x['scenario']==name]
            assert len(cohort)==16
            case_records.append({'seed':seed,'scenario':name,
              'central_formed':sum(x['central_optimal_pairs'] for x in cohort),
              'chronological_formed':sum(x['chronological_first_accept']['n_pairs'] for x in cohort),
              'reverse_formed':sum(x['reverse_chronological_first_accept']['n_pairs'] for x in cohort),
              'tick_count':len(cohort)})
    report={'schema':'N347_CENTRAL_VS_DECENTRAL_CONDITIONAL_SHADOW',
      'native_original_event_index_SHA':sha(nidx), 'frozen_input_manifest_SHA':sha(inpath),
      'cases':case_records,'ticks':ticks,
      'matching_ticks':len(ticks),
      'central_total_pairs':sum(x['central_optimal_pairs'] for x in ticks),
      'chronological_total_pairs':sum(x['chronological_first_accept']['n_pairs'] for x in ticks),
      'reverse_total_pairs':sum(x['reverse_chronological_first_accept']['n_pairs'] for x in ticks),
      'chronological_strict_cardinality_loss_ticks':sum(x['chronological_first_accept']['lost_pairs_vs_central']>0 for x in ticks),
      'reverse_strict_cardinality_loss_ticks':sum(x['reverse_chronological_first_accept']['lost_pairs_vs_central']>0 for x in ticks),
      'chronological_pair_identity_diff_ticks':sum(not x['chronological_first_accept']['identical_pair_set'] for x in ticks),
      'reverse_pair_identity_diff_ticks':sum(not x['reverse_chronological_first_accept']['identical_pair_set'] for x in ticks),
      'forward_vs_reverse_diff_ticks':sum(not x['reverse_vs_forward_pair_sets_identical'] for x in ticks),
      'adversarial_self_edge_detected':True,
      'caveat':'CONDITIONAL SHADOW, not independent longitudinal world: accepted native decisions/visibilities are held fixed from centralized ESBM, but after immediate pairing actual subsequent exposures and decisions would be different. Synthetic outcomes only; no empirical human validation or causal inference on real dating markets.',
      'CT2_scientific':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N347_ALLOCATION_SHADOW','ticks',report['matching_ticks'],
      'central',report['central_total_pairs'],
      'forward',report['chronological_total_pairs'],
      'reverse',report['reverse_total_pairs'],
      'forward_card_loss_ticks',report['chronological_strict_cardinality_loss_ticks'],
      'pair_identity_diff',report['chronological_pair_identity_diff_ticks'],
      'SHA',sha(OUT))

if __name__=='__main__':main()
