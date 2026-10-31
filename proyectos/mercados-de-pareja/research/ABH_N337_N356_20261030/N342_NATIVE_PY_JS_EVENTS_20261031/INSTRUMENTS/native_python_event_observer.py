"""N342 noninvasive CPython line tracer over byte-identical original ESBM simulate.

Only observes named original source lines and wraps NetworkX matching without
modifying the historical Python file. Produces original directed events and
pair identity by tick. All 60 original people(seed) shocks are frozen from N341.
"""
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT.parent/'ESBM_AUDIT_N337_20261031'/'esbm_dynamic.py'
DIR=ROOT/'outcomes'/'N342_NATIVE_TRACES'
ORIG_SHA='f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
SEEDS=[101,211,307,401,503,601]
NAMES=['mixed_random','heterosexual_restricted','institutional_segregation',
  'explicit_norm_preference','popularity_ranking','visibility_balancing',
  'private_rejection_learning','public_rejection_signal',
  'longer_partnerships','shorter_partnerships']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if DIR.exists() or (ROOT/'outcomes'/'N342_NATIVE_INDEX.json').exists():
        raise SystemExit('N342_OUTPUTS_ALREADY_EXIST')
    assert sha(SRC)==ORIG_SHA
    frozen=json.loads((ROOT/'N341_INPUT_MANIFEST.json').read_text(encoding='utf8'))
    assert sha(ROOT/'N341_INPUT_MANIFEST.json')=='84a52580add085ab551dacf6e4cd3fdfc80be8eeaf187c7d3e4b25be208e42bf'
    assert frozen['seed_order']==SEEDS and frozen['scenario_order']==NAMES
    spec=importlib.util.spec_from_file_location('original_ESBM_N342_untouched',SRC)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert (mod.N,mod.STEPS,mod.K)==(144,16,7)
    assert mod.simulate.__code__.co_firstlineno==63
    DIR.mkdir(parents=True)
    index=[]
    for seed in SEEDS:
        p=mod.people(seed)
        entry=next(z for z in frozen['rows'] if z['seed']==seed)
        people={k:p[k].tolist() for k in ['genders','scopes','norm','q','age']}
        fpath=ROOT/'official_inputs_60'/entry['people']['path']
        assert sha(fpath)==entry['people']['sha256']
        assert json.loads(fpath.read_text(encoding='utf8'))==people
        for kind in ['u_send','u_reply','u_hazard','u_expose','u_match']:
            f=ROOT/'official_inputs_60'/entry['tensors'][kind]['path']
            assert sha(f)==entry['tensors'][kind]['sha256']
            assert np.array_equal(p[kind],np.fromfile(f,dtype='<f8').reshape((16,144,144)))
        # Reuse same actual original arrays for 10 configurations; original simulate remains unchanged.
        mod.people=lambda _seed,data=p:data
        for name in NAMES:
            t0=time.monotonic()
            output=DIR/f'{seed}_{name}.jsonl'
            summary_file=DIR/f'{seed}_{name}.json'
            event_sha=hashlib.sha256()
            event_count=0;matches=[];events_by_stage={}
            original_match=mod.nx.algorithms.matching.max_weight_matching
            def match_hook(graph,*args,**kwargs):
                picked=original_match(graph,*args,**kwargs)
                pairs=sorted(tuple(sorted((int(i),int(j)))) for i,j in picked)
                matches.append([list(edge) for edge in pairs])
                return picked
            mod.nx.algorithms.matching.max_weight_matching=match_hook
            try:
                with output.open('x',encoding='utf8',newline='\n') as fd:
                    def record(e):
                        nonlocal event_count
                        e['seed']=seed;e['scenario']=name
                        line=json.dumps(e,separators=(',',':'),allow_nan=False)+'\n'
                        fd.write(line);event_sha.update(line.encode('utf8'))
                        events_by_stage[e['stage']]=events_by_stage.get(e['stage'],0)+1
                        event_count+=1
                    def watch(frame,event,arg):
                        if event!='line':return watch
                        line=frame.f_lineno
                        if line not in (87,108,114,118):return watch
                        f=frame.f_locals
                        t=int(f['t']);i=int(f['i']);j=int(f['j'])
                        if line==87:
                            u=float(f['uh'][t,i,j]);prob=float(f['h'])
                            record({'t':t,'stage':'dissolution','i':i,'j':j,
                                'decision':bool(u<prob),'u':u,'p':prob})
                        elif line==108:
                            exposure_u=float(f['p']['u_expose'][t,i,j])
                            record({'t':t,'stage':'exposure','i':i,'j':j,
                                'decision':None,'u_expose':exposure_u})
                        elif line==114:
                            u=float(f['u_send'][t,i,j]);prob=float(mod.sigmoid(f['send_util']))
                            record({'t':t,'stage':'proposal','i':i,'j':j,
                                'decision':bool(u<prob),'u':u,'p':prob})
                        elif line==118:
                            u=float(f['u_reply'][t,j,i]);prob=float(mod.sigmoid(f['reply_util']))
                            record({'t':t,'stage':'response','i':i,'j':j,
                                'decision':bool(u<prob),'u':u,'p':prob})
                        return watch
                    def dispatcher(frame,event,arg):
                        if event=='call' and frame.f_code is mod.simulate.__code__:
                            return watch
                        return None
                    sys.settrace(dispatcher)
                    try:
                        row=mod.simulate(seed,name,mod.SCENARIOS[name])
                    finally:
                        sys.settrace(None)
                assert len(matches)==16
                obj={'seed':seed,'scenario':name,'status':'EXECUTED',
                     'result':row,'formation_pairs_by_tick':matches,
                     'directed_events':event_count,'by_stage':events_by_stage,
                     'wall_ms':round((time.monotonic()-t0)*1000,3)}
                summary_file.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')
                index.append({'seed':seed,'scenario':name,'status':obj['status'],
                  'run_path':summary_file.relative_to(DIR.parent).as_posix(),
                  'run_sha256':sha(summary_file),
                  'trace_path':output.relative_to(DIR.parent).as_posix(),
                  'trace_sha256':sha(output),
                  'event_sha_stream':event_sha.hexdigest(),
                  'directed_events':event_count,'by_stage':events_by_stage,
                  'matching_ticks':len(matches),'wall_ms':obj['wall_ms']})
            finally:
                sys.settrace(None)
                mod.nx.algorithms.matching.max_weight_matching=original_match
    assert len(index)==60
    manifest={'schema':'N342_NATIVE_PY_ORIGINAL_DIRECTED_EVENT_INDEX',
      'original_source_sha256':ORIG_SHA,'source_observer_sha256':sha(__file__),
      'original_inputs_sha256':sha(ROOT/'N341_INPUT_MANIFEST.json'),
      'rows':index,'runs':len(index),
      'directed_events':sum(x['directed_events'] for x in index),
      'matching_ticks':sum(x['matching_ticks'] for x in index)}
    out=ROOT/'outcomes'/'N342_NATIVE_INDEX.json'
    out.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print('N342_NATIVE_COMPLETE',manifest['runs'],'runs',manifest['directed_events'],
      'directed',manifest['matching_ticks'],'ticks','SHA',sha(out))

if __name__=='__main__':main()
