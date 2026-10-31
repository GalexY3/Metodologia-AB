"""N340 comparison: exact individual original Python result+matching vs polynomial TS.
N338 native Python runs are reused byte-identically; not rerun to consume a slot.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REF=ROOT.parent/'ESBM_AUDIT_N337_20261031'/'N338_PY_OFFICIAL.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def diff(a,b,path='$'):
    if a is None or b is None:return None if a is b else {'path':path,'expected':a,'observed':b}
    if isinstance(a,bool) or isinstance(b,bool):return None if a is b else {'path':path,'expected':a,'observed':b}
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        tolerance=0 if isinstance(a,int) and isinstance(b,int) else 1e-9
        return None if math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tolerance else {'path':path,'expected':a,'observed':b,'abs_error':abs(a-b)}
    if isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):return {'path':path+'.length','expected':len(a),'observed':len(b)}
        for i,(x,y) in enumerate(zip(a,b)):
            z=diff(x,y,path+'.'+str(i))
            if z:return z
        return None
    if isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys():return {'path':path+'.keys','expected':sorted(a),'observed':sorted(b)}
        for k in a:
            z=diff(a[k],b[k],path+'.'+k)
            if z:return z
        return None
    return None if a==b else {'path':path,'expected':a,'observed':b}

def main():
    assert sha(REF)=='b95e2727af8eecf54f52e026531ce7adc6686e73cd2f203fe804f60e728ed48d'
    raw=ROOT/'outcomes'/'N340_POLY_OFFICIAL_FULL.json'
    rows=json.loads(raw.read_text(encoding='utf8'))['rows']
    py=json.loads(REF.read_text(encoding='utf8'))['runs']
    assert len(py)==len(rows)==2
    out=[]
    for a,b in zip(py,rows):
        assert a['seed']==b['seed']==101 and a['scenario']==b['scenario']
        if b['status']!='EXECUTED':
            first={'status':'JS_RESOURCE_OR_EXECUTION_FAILURE','error':b.get('error')}
        else:
            first=diff(a['formation_pairs_by_tick'],b['formation_pairs_by_tick'],'$.formation_pairs_by_tick') or diff(a['result'],b['result'],'$.result')
        cert=all(x['certified'] and x['certificate'] and x['certificate']['certified'] for x in b['matching'])
        out.append({'scenario':a['scenario'],'status':b['status'],
                    'pairticks_python':len(a['formation_pairs_by_tick']),
                    'pairticks_js':len(b['formation_pairs_by_tick']),
                    'matched_pairs_per_tick':len(a['formation_pairs_by_tick'])==len(b['formation_pairs_by_tick']) and all(x==y for x,y in zip(a['formation_pairs_by_tick'],b['formation_pairs_by_tick'])),
                    'full_result_and_pair_parity':first is None,'first_divergence':first,
                    'all_matching_certificates_present':cert,
                    'certificates':len(b['matching']),'directed_events_stored':len(b['directed']),
                    'matching_graphs_sha256':b['graphShas'],
                    'elapsed_ms':b['elapsed_ms']})
    dest=ROOT/'outcomes'/'N340_COMPARED.json'
    if dest.exists():raise SystemExit('NO_OVERWRITE')
    report={'schema':'ABH_N340_COMPARISON', 'reference_sha256':sha(REF),
            'js_source_sha256':sha(raw),'checks':out,
            'complete_parity':sum(x['full_result_and_pair_parity'] for x in out),
            'full_runs_js':sum(x['status']=='EXECUTED' for x in out),
            'certified_matching_ticks':sum(x['certificates'] for x in out if x['all_matching_certificates_present']),
            'human_observations':0,'CT2':7,'R5':'STOP'}
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N340_COMPARED',report['complete_parity'],'/2',report['full_runs_js'],'complete TS',report['certified_matching_ticks'],'cert ticks')

if __name__=='__main__':main()
