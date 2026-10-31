"""Custody-only hash index for 54 completed N341 runs after process interruption.

Does NOT execute any ESBM or compute new matching outcomes.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
RUNS=ROOT/'outcomes'/'N341_TRACES'
SEEDS=[101,211,307,401,503,601]
NAMES=['mixed_random','heterosexual_restricted','institutional_segregation',
 'explicit_norm_preference','popularity_ranking','visibility_balancing',
 'private_rejection_learning','public_rejection_signal',
 'longer_partnerships','shorter_partnerships']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    out=ROOT/'N341_PARTIAL_54_MANIFEST.json'
    if out.exists() or (ROOT/'outcomes'/'N341_TS60_INDEX.json').exists():
        raise SystemExit('MANIFEST_OR_FINAL_ALREADY_EXISTS')
    expected=[(s,n) for s in SEEDS for n in NAMES]
    present=[]
    for seed,name in expected:
        f=RUNS/f'{seed}_{name}.json'
        t=RUNS/f'{seed}_{name}.jsonl'
        if not f.exists() and not t.exists():continue
        assert f.exists() and t.exists(),('PARTIAL_FILE_PAIR',seed,name)
        row=json.loads(f.read_text(encoding='utf8'))
        assert (row['seed'],row['scenario'])==(seed,name)
        assert row['status']=='EXECUTED'
        assert len(row['formation_pairs_by_tick'])==16
        assert len(row['matching'])==16
        assert all(x['certified'] and x['certificate']['certified'] for x in row['matching'])
        present.append({'seed':seed,'scenario':name,'run_sha256':sha(f),'trace_sha256':sha(t),
                        'run_bytes':f.stat().st_size,'trace_bytes':t.stat().st_size,
                        'matching_ticks':16,'directed_events':row['directed_count'],
                        'total_events':row['event_count'],'elapsed_ms':row['elapsed_ms']})
    assert len(present)==54,('EXPECTED_54_COMPLETED',len(present))
    assert [(x['seed'],x['scenario']) for x in present]==expected[:54]
    body={'schema':'N341_INTERRUPTED_FIRST54_HASH_CUSTODY','status':'54_COMPLETED_6_NOT_STARTED',
          'cause':'PowerShell Process.WaitForExit blocked with redirected stdout; process killed after confirming unchanged 54 outputs',
          'not_counted_as_new_AB_cycle':True,'frozen_original_JS_runner_sha256':sha(ROOT/'instrument'/'run_poly_60.mjs'),
          'frozen_original_input_manifest_sha256':sha(ROOT/'N341_INPUT_MANIFEST.json'),
          'rows':present,'unstarted':[{'seed':s,'scenario':n} for s,n in expected[54:]]}
    out.write_text(json.dumps(body,indent=2)+'\n',encoding='utf8')
    print('CUSTODY_PARTIAL',len(present),'last',present[-1]['seed'],present[-1]['scenario'],
          'remaining',len(body['unstarted']),'SHA',sha(out))

if __name__=='__main__':main()
