"""N342 event-by-event comparator native Python lines vs JS directed events.

Hard fails on chronology/actors, shock or decision; float tolerance 1e-12 for p.
Includes an adversarial swapped-actor control and threshold bit-flip detector.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
NATIVE=ROOT/'outcomes'/'N342_NATIVE_INDEX.json'
JS=ROOT/'outcomes'/'N341_TS60_INDEX.json'
EXPECTED_JS_SHA='37b8a1010968e0ead1a13f7f71193858bcfb83b0e3428573ad734f96e136948d'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def difference(a,b):
    for key in ['seed','scenario','t','stage','i','j','decision']:
        x,y=a.get(key),b.get(key)
        if x!=y:return {'code':'DIRECTED_DECISION_OR_COORDINATE_DIFFERENCE',
                         'field':key,'expected':x,'observed':y}
    if a['stage']=='exposure':
        # JS exposure event does not serialize source Gumbel shock (available in frozen tensor).
        if not isinstance(a.get('u_expose'),float) or not 0<=a['u_expose']<1:
            return {'code':'MISSING_PY_EXPOSURE_SHOCK','field':'u_expose'}
    else:
        for key in ['u','p']:
            x,y=a.get(key),b.get(key)
            if not isinstance(x,(int,float)) or not isinstance(y,(int,float)):
                return {'code':'SHOCK_OR_PROBABILITY_MISSING','field':key}
            tol=0 if key=='u' else 1e-12
            if not math.isfinite(x) or not math.isfinite(y) or abs(x-y)>tol:
                return {'code':'SHOCK_OR_PROBABILITY_DIFFERENCE','field':key,
                        'expected':x,'observed':y,'abs_error':abs(x-y)}
    return None

def result_difference(x,y,path='$'):
    if x is None or y is None:return None if x is y else {'path':path,'expected':x,'observed':y}
    if isinstance(x,bool) or isinstance(y,bool):return None if x is y else {'path':path,'expected':x,'observed':y}
    if isinstance(x,(float,int)) and isinstance(y,(float,int)):
        tol=0 if isinstance(x,int) and isinstance(y,int) else 1e-9
        return None if math.isfinite(x) and math.isfinite(y) and abs(x-y)<=tol else {'path':path,'expected':x,'observed':y}
    if isinstance(x,list) and isinstance(y,list):
        if len(x)!=len(y):return {'path':path+'.length','expected':len(x),'observed':len(y)}
        for i,(a,b) in enumerate(zip(x,y)):
            d=result_difference(a,b,path+'.'+str(i))
            if d:return d
        return None
    if isinstance(x,dict) and isinstance(y,dict):
        if set(x)!=set(y):return {'path':path+'.keys','expected':sorted(x),'observed':sorted(y)}
        for k in sorted(x):
            d=result_difference(x[k],y[k],path+'.'+k)
            if d:return d
        return None
    return None if x==y else {'path':path,'expected':x,'observed':y}

def main():
    target=ROOT/'outcomes'/'N342_NATIVE_JS_COMPARE.json'
    if target.exists():raise SystemExit('NO_OUTPUT_OVERWRITE')
    assert sha(JS)==EXPECTED_JS_SHA
    py=json.loads(NATIVE.read_text(encoding='utf8'))['rows']
    ts=json.loads(JS.read_text(encoding='utf8'))['rows']
    assert len(py)==len(ts)==60
    report=[]; first_pair=None
    for x,y in zip(py,ts):
        assert (x['seed'],x['scenario'])==(y['seed'],y['scenario'])
        pf=ROOT/'outcomes'/x['run_path'];tf=ROOT/'outcomes'/y['run_file']
        pe=ROOT/'outcomes'/x['trace_path'];te=ROOT/'outcomes'/y['trace_file']
        assert sha(pf)==x['run_sha256'] and sha(tf)==y['run_sha256']
        assert sha(pe)==x['trace_sha256'] and sha(te)==y['trace_sha256']
        a=json.loads(pf.read_text(encoding='utf8'))
        b=json.loads(tf.read_text(encoding='utf8'))
        mismatch=result_difference(a['formation_pairs_by_tick'],b['formation_pairs_by_tick'],'$.pairs_by_tick') or result_difference(a['result'],b['result'],'$.result')
        n=0;direct_diff=None
        with pe.open(encoding='utf8') as fa,te.open(encoding='utf8') as fb:
            while True:
                v,w=fa.readline(),fb.readline()
                if not v and not w:break
                if not v or not w:
                    direct_diff={'code':'DIRECTED_TRACE_LENGTH_DIFFERENCE','event_index':n,'python_end':not v,'typescript_end':not w}
                    break
                obs,js=json.loads(v),json.loads(w)
                d=difference(obs,js)
                if d:
                    direct_diff={'event_index':n,**d,
                                 'observed_python':obs,'observed_typescript':js}
                    break
                n+=1
        report.append({'seed':x['seed'],'scenario':x['scenario'],
          'pairs_and_summary_equal':mismatch is None,'pairs_first_difference':mismatch,
          'directed_trace_equal':direct_diff is None,'directed_first_difference':direct_diff,
          'directed_events_compared':n,'python_directed_total':x['directed_events'],
          'ts_directed_total':y['directed_events'],
          'matching_ticks':len(a['formation_pairs_by_tick'])})
    first=json.loads((ROOT/'outcomes'/py[0]['trace_path']).open(encoding='utf8').readline())
    mutation=json.loads(json.dumps(first));mutation['i']=int(mutation['i'])+1
    detected=difference(first,mutation)
    assert detected and detected['field']=='i'
    # Swap a proposal/response event's decision without altering the shock/probability.
    if first['stage'] in ('proposal','response','dissolution'):
        row=first
    else:
        with (ROOT/'outcomes'/py[0]['trace_path']).open(encoding='utf8') as fh:
            row=next(json.loads(line) for line in fh if json.loads(line)['stage']=='proposal')
    decision_mut=json.loads(json.dumps(row));decision_mut['decision']=not row['decision']
    dd=difference(row,decision_mut)
    assert dd and dd['field']=='decision'
    result={'schema':'N342_NATIVE_PY_JS_EVENTS_PAIR_PARITY',
      'original_observer_source_sha256':json.loads(NATIVE.read_text(encoding='utf8'))['source_observer_sha256'],
      'Python_index_sha256':sha(NATIVE),'TS_index_sha256':sha(JS),
      'cases':report,
      'individual_full_pairs_and_result_parity':sum(x['pairs_and_summary_equal'] for x in report),
      'individual_directed_event_parity':sum(x['directed_trace_equal'] for x in report),
      'directed_events_compared_total':sum(x['directed_events_compared'] for x in report),
      'matching_ticks_checked':sum(x['matching_ticks'] for x in report),
      'mutation_actor_detected_field':detected['field'],
      'mutation_decision_detected_field':dd['field'],
      'CT2':7,'STOP_R5_human':True,'synthetic_only':True}
    target.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N342_NATIVE_COMPARISON',result['individual_full_pairs_and_result_parity'],'/60 pairs/results',
      result['individual_directed_event_parity'],'/60 directed',
      result['directed_events_compared_total'],'event matches',
      result['matching_ticks_checked'],'ticks','SHA',sha(target))

if __name__=='__main__':main()
