"""Prespecified comparator for one seed and two official ESBM trajectories."""
import hashlib
import json
from pathlib import Path

from audit_n337 import diff

ROOT=Path(__file__).resolve().parent


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    a=json.loads((ROOT/'N338_PY_OFFICIAL.json').read_text(encoding='utf-8'))['runs']
    b=json.loads((ROOT/'N338_TS_OFFICIAL.json').read_text(encoding='utf-8'))['runs']
    assert len(a)==len(b)==2
    checks=[]
    for x,y in zip(a,b):
        assert x['seed']==y['seed']==101 and x['scenario']==y['scenario']
        error={'code':'TS_RESOURCE_OR_EXECUTION_NEGATIVE','detail':y.get('error'),
               'event':y.get('last_event')} if y['status']!='EXECUTED' else (
               diff(x['formation_pairs_by_tick'],y['formation_pairs_by_tick'],'$.formed_pairs') or
               diff(x['result'],y['result'],'$.result'))
        checks.append({'scenario':x['scenario'],'status':y['status'],
                       'first_difference':error,'pair_ticks_py':len(x['formation_pairs_by_tick']),
                       'pair_ticks_ts':len(y['formation_pairs_by_tick']),
                       'ts_emitted_events':y['emitted_events'],'ts_matching_status':y['matching_status']})
    report={'schema':'ABH_N338_N207_TS_VS_TRUE_ESBM_N144_T16_K7',
            'original_python_sha256':sha(ROOT/'esbm_dynamic.py'),
            'official_input_manifest_sha256':sha(ROOT/'N338_INPUT_MANIFEST.json'),
            'native_sha256':sha(ROOT/'N338_PY_OFFICIAL.json'),
            'typescript_sha256':sha(ROOT/'N338_TS_OFFICIAL.json'),
            'checks':checks,'successful_pair_and_full_output':sum(x['first_difference'] is None for x in checks),
            'resource_errors_or_divergences':sum(x['first_difference'] is not None for x in checks),
            'historical_N237_TypeScript_executed':False,'CT2_scientific':7,'STOP_R5_human':True}
    dest=ROOT/'N338_AUDIT.json'
    if dest.exists(): raise SystemExit('OUTPUT_PREEXISTS')
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('N338_AUDIT',report['successful_pair_and_full_output'],'/2',
          'divergences',report['resource_errors_or_divergences'],sha(dest))


if __name__=='__main__':main()
