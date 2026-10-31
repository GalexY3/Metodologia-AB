"""N354 descriptive *paired* synthetic full-dynamic institution comparison.
No human inference. Uses frozen central and chronological/reverse immediate
acceptance worlds; DA candidate worlds recompute opportunities and responses.
"""
from pathlib import Path
import hashlib,json,statistics
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outcomes'
INDEX=OUT/'N354_DA_DYNAMIC_INDEX.json'
DEST=OUT/'N354_FULL_DYNAMIC_DA_COMPARISON.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(p):return {tuple(sorted(z)) for z in p}
def main():
    if DEST.exists():raise SystemExit('NO_OVERWRITE')
    central=json.loads((OUT/'N341_TS60_INDEX.json').read_text())['rows']
    greedy=json.loads((OUT/'N348_DECENTRALIZED_INDEX.json').read_text())['rows']
    da=json.loads(INDEX.read_text())['rows']
    assert len(da)==12 and len(central)==60 and len(greedy)==120
    assert sha(OUT/'N341_TS60_INDEX.json')=='37b8a1010968e0ead1a13f7f71193858bcfb83b0e3428573ad734f96e136948d'
    assert sha(OUT/'N348_DECENTRALIZED_INDEX.json')=='e357e134c23379c07ed8aa52be1924401d664f951e55829428b8cc94083d5f28'
    records=[]
    for seed in [101,211,307,401,503,601]:
      c=next(x for x in central if x['seed']==seed and x['scenario']=='heterosexual_restricted')
      assert sha(OUT/c['run_file'])==c['run_sha256']
      cobj=json.loads((OUT/c['run_file']).read_text())
      for order in ['chronological','reverse']:
        d=next(x for x in da if x['seed']==seed and x['scenario']=='heterosexual_restricted' and x['order']==order)
        g=next(x for x in greedy if x['seed']==seed and x['scenario']=='heterosexual_restricted' and x['order']==order)
        for q in (d,g):assert sha(OUT/q['run_file'])==q['run_sha256']
        dj=json.loads((OUT/d['run_file']).read_text())
        gj=json.loads((OUT/g['run_file']).read_text())
        if dj['status']!='EXECUTED':
          records.append({'seed':seed,'side':d['order'],'status':'NEGATIVE','error':dj.get('error')});continue
        assert len(dj['formation_pairs_by_tick'])==len(gj['formation_pairs_by_tick'])==len(cobj['formation_pairs_by_tick'])==16
        assert len(dj['matchingDiagnostics'])==16
        assert all(v['meta']['blocking_pairs']==0 for v in dj['matchingDiagnostics'])
        assert all(v['meta']['proposer_side']==('F' if order=='chronological' else 'M') for v in dj['matchingDiagnostics'])
        assert sha(OUT/d['trace_file'])==d['trace_sha256']
        jaccard=[]
        for x,y in zip(dj['formation_pairs_by_tick'],cobj['formation_pairs_by_tick']):
            a,b=canonical(x),canonical(y)
            jaccard.append(len(a&b)/len(a|b) if a or b else 1.0)
        records.append({'seed':seed,'side':'F' if order=='chronological' else 'M',
          'status':'EXECUTED','central_formed':cobj['result']['total_relationships_formed'],
          'DA_formed':dj['result']['total_relationships_formed'],
          'greedy_same_order_formed':gj['result']['total_relationships_formed'],
          'DA_minus_central':dj['result']['total_relationships_formed']-cobj['result']['total_relationships_formed'],
          'DA_minus_greedy':dj['result']['total_relationships_formed']-gj['result']['total_relationships_formed'],
          'DA_versus_central_pair_jaccard_mean':sum(jaccard)/len(jaccard),
          'DA_matching_certified_stability_ticks':len(dj['matchingDiagnostics']),
          'DA_directed_events':d['directed_events']})
    result={'schema':'ABH_N354_DA_FM_FULL_DYNAMIC_PAIRED_SYNTHETIC',
      'DA_index_sha':sha(INDEX),'complete_runs':sum(r['status']=='EXECUTED' for r in records),
      'negative_runs':[r for r in records if r['status']!='EXECUTED'],
      'records':records,'summary':{}}
    for side in ['F','M']:
      group=[r for r in records if r['side']==side and r['status']=='EXECUTED']
      result['summary'][side]={
        'runs':len(group),'DA_total_formed':sum(r['DA_formed'] for r in group),
        'central_total_formed':sum(r['central_formed'] for r in group),
        'greedy_total_formed':sum(r['greedy_same_order_formed'] for r in group),
        'DA_minus_central_total':sum(r['DA_minus_central'] for r in group),
        'DA_minus_greedy_total':sum(r['DA_minus_greedy'] for r in group),
        'mean_pair_jaccard':sum(r['DA_versus_central_pair_jaccard_mean'] for r in group)/len(group) if group else None}
    result['scope']='Entire subsequent 16-tick synthetic world replays. Preference rankings separately ASSUMED; F/M proposer treatment requires heterosexual FM_only. Six seeds not independent human units; no causal claim about dating markets.'
    result['CT2_scientific']=7;result['STOP_R5_human']=True
    DEST.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N354_DA_DYNAMIC',result['summary'],'COMPLETE',result['complete_runs'],'/12','SHA',sha(DEST))
if __name__=='__main__':main()
