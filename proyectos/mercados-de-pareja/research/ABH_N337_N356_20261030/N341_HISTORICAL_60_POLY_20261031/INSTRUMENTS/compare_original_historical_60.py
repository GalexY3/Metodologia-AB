"""N341 complete per-run scalar/track comparison against HISTORIC original ESBM RUNS.

Uses an existing frozen historical output; this is a software regression check,
not an ex ante human holdout. The history file is decoded only after prereg.
"""
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
FROZEN_HISTORY=ROOT/'HISTORICAL_ESBM_RUNS.json.gz.b64'
INDEX=ROOT/'outcomes'/'N341_TS60_INDEX.json'
FROZEN_KEYS=[101,211,307,401,503,601]
NAMES=['mixed_random','heterosexual_restricted','institutional_segregation',
  'explicit_norm_preference','popularity_ranking','visibility_balancing',
  'private_rejection_learning','public_rejection_signal',
  'longer_partnerships','shorter_partnerships']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def diff(x,y,path='$'):
    if x is None or y is None:return None if x is y else {'path':path,'expected':x,'observed':y}
    if isinstance(x,bool) or isinstance(y,bool):return None if x is y else {'path':path,'expected':x,'observed':y}
    if isinstance(x,(int,float)) and isinstance(y,(int,float)):
        tolerance=0 if isinstance(x,int) and isinstance(y,int) else 1e-9
        return None if math.isfinite(x) and math.isfinite(y) and abs(x-y)<=tolerance else {'path':path,'expected':x,'observed':y,'abs_error':abs(x-y)}
    if isinstance(x,list) and isinstance(y,list):
        if len(x)!=len(y):return {'path':path+'.length','expected':len(x),'observed':len(y)}
        for i,(a,b) in enumerate(zip(x,y)):
            d=diff(a,b,path+'.'+str(i))
            if d:return d
        return None
    if isinstance(x,dict) and isinstance(y,dict):
        if x.keys()!=y.keys():return {'path':path+'.keys','expected':sorted(x),'observed':sorted(y)}
        for k in x:
            d=diff(x[k],y[k],path+'.'+k)
            if d:return d
        return None
    return None if x==y else {'path':path,'expected':x,'observed':y}

def main():
    out=ROOT/'outcomes'/'N341_HISTORIC_PARITY.json'
    if out.exists():raise SystemExit('NO_OVERWRITE')
    history=json.loads(gzip.decompress(base64.b64decode(FROZEN_HISTORY.read_bytes())))
    assert isinstance(history,list) and len(history)==60
    manifest=json.loads(INDEX.read_text(encoding='utf8'))
    assert len(manifest['rows'])==60 and manifest['expected_runs']==60
    expected=[(seed,name) for seed in FROZEN_KEYS for name in NAMES]
    assert [(x['seed'],x['scenario']) for x in history]==expected
    assert [(x['seed'],x['scenario']) for x in manifest['rows']]==expected
    rows=[]
    for original,entry in zip(history,manifest['rows']):
        file=ROOT/'outcomes'/entry['run_file']
        actual=json.loads(file.read_text(encoding='utf8'))
        assert sha(file)==entry['run_sha256']
        trace=ROOT/'outcomes'/entry['trace_file']
        assert sha(trace)==entry['trace_sha256']
        assert (actual['seed'],actual['scenario'])==(original['seed'],original['scenario'])
        mismatch=diff(original,actual['result'],'$.result') if actual['status']=='EXECUTED' else {'path':'$.execution','error':actual['error']}
        rows.append({'seed':actual['seed'],'scenario':actual['scenario'],'status':actual['status'],
          'full_result_parity':mismatch is None,'first_difference':mismatch,
          'directed_events':entry['directed_events'],
          'pair_ticks':entry['formation_ticks'],
          'certified_matching_ticks':entry['matching_certified'],
          'run_sha256':entry['run_sha256'],'trace_sha256':entry['trace_sha256']})
    # Adversarial in-memory perturbation: an altered historical integer must not escape.
    mut=json.loads(json.dumps(history[0]))
    mut['total_impressions']+=1
    detected=diff(history[0],mut,'$.history')
    assert detected and detected['path']=='$.history.total_impressions'
    report={'schema':'ABH_N341_HISTORICAL_60_COMPARE',
       'historic_b64_sha256':sha(FROZEN_HISTORY),
       'TS_index_sha256':sha(INDEX),
       'historic_source_record':'original RUNS.json.gz.b64 Git blob d8dbf04ec52337d46892e555cceee49ef224efc6',
       'runs':rows,'full_result_parity_count':sum(x['full_result_parity'] for x in rows),
       'complete_ts_count':sum(x['status']=='EXECUTED' for x in rows),
       'certified_matching_ticks':sum(x['certified_matching_ticks'] for x in rows),
       'directed_ts_events_stored':sum(x['directed_events'] for x in rows),
       'synthetic_only':True,'no_native_original_directed_trace':True,
       'history_origin_outcomes_preexist_this_prereg':True,
       'adversarial_mutation_path':detected['path'],
       'CT2':7,'human_R5':'STOP'}
    out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N341_HISTORIC_PARITY',report['full_result_parity_count'],'/60',
      'JS_full',report['complete_ts_count'],'/60',
      'certified_matching_ticks',report['certified_matching_ticks'],
      'directed_ts_events',report['directed_ts_events_stored'],
      'SHA',sha(out))

if __name__=='__main__':main()
