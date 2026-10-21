#!/usr/bin/env python3
"""50 deterministic infrastructure/adversarial checks for AB-E2E-01.
No LLM agents, BixBench scoring or evidence of scientific superiority.
"""
from __future__ import annotations
import csv, hashlib, json, sys, time, tempfile
from collections import Counter
from pathlib import Path

from benchmark_ab import prepare, read_csv, write_csv, blinded, analyze

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'pilot_50_2026-10-21'; OUT.mkdir(exist_ok=True)
CASES=[
    ('deterministic_assignment', 'accept'),
    ('inventory_order_invariance','accept'),
    ('balanced_and_blinded','accept'),
    ('duplicate_task_id','reject'),
    ('insufficient_clusters','reject'),
    ('missing_grading','reject'),
    ('duplicate_grading','reject'),
    ('invalid_score','reject'),
    ('missing_arm','reject'),
    ('equal_scores_zero_effect','accept'),
]

def fixture(tmp: Path, seed: str, n=9):
    tasks=[{'task_id':f'q{i:02}', 'cluster_id':f'capsule_{i:02}', 'benchmark':'BixBench'} for i in range(n)]
    inv=tmp/'inventory.csv'; write_csv(inv,tasks,['task_id','cluster_id','benchmark'])
    run=tmp/'runs'; prepare(inv,run,seed,6,2,'BixBench')
    assignments=run/'assignments_RESTRICTED.csv'; rows=read_csv(assignments)
    return tasks,inv,assignments,rows

def expect_error(f,part=None):
    try:f()
    except (ValueError, KeyError) as e:
        if part and part.lower() not in str(e).lower():raise AssertionError(f'Wrong rejection reason: {e}')
        return
    raise AssertionError('Invalid input was accepted')

def check(test,variation,tmp):
    seed=f'AUDIT50-{variation:02}-{test}'
    tasks,inv,ap,rows=fixture(tmp,seed)
    if test=='deterministic_assignment':
        prepare(inv,tmp/'repeat',seed,6,2,'BixBench')
        assert ap.read_bytes()==(tmp/'repeat'/'assignments_RESTRICTED.csv').read_bytes()
        assert hashlib.sha256(ap.read_bytes()).hexdigest()==hashlib.sha256((tmp/'repeat'/'assignments_RESTRICTED.csv').read_bytes()).hexdigest()
    elif test=='inventory_order_invariance':
        write_csv(tmp/'perm_inv.csv',list(reversed(tasks)),['task_id','cluster_id','benchmark'])
        prepare(tmp/'perm_inv.csv',tmp/'permuted',seed,6,2,'BixBench')
        assert ap.read_bytes()==(tmp/'permuted'/'assignments_RESTRICTED.csv').read_bytes()
    elif test=='balanced_and_blinded':
        assert len(rows)==24
        assert Counter(r['arm'] for r in rows)=={'AB':12,'BASELINE':12}
        gr=(ap.parent/'grader_manifest_BLIND.csv').read_text()
        assert 'arm' not in gr and 'order_key' not in gr
        sub=tmp/'submissions.csv';write_csv(sub,[{'run_id':r['run_id'],'answer':'ordinary answer'} for r in rows],['run_id','answer'])
        blinded(sub,ap,tmp/'blind.csv')
        assert 'arm' not in (tmp/'blind.csv').read_text()
    elif test=='duplicate_task_id':
        bad=tasks+[dict(tasks[variation])];b=tmp/'bad.csv';write_csv(b,bad,['task_id','cluster_id','benchmark'])
        expect_error(lambda:prepare(b,tmp/'invalid',seed,6,2,'BixBench'),'Duplicate')
    elif test=='insufficient_clusters':
        expect_error(lambda:prepare(inv,tmp/'invalid',seed,99,2,'BixBench'),'Need')
    else:
        score_rows=[{'run_id':r['run_id'],'score':'0.5'} for r in rows]
        if test=='missing_grading':score_rows.pop(variation)
        elif test=='duplicate_grading':score_rows.append(dict(score_rows[variation]))
        elif test=='invalid_score':score_rows[variation]['score']=['NaN','inf','-0.01','1.01','abc'][variation]
        elif test=='missing_arm':
            ass=rows.copy();ass.pop(next(i for i,r in enumerate(ass) if r['arm']=='AB'))
            write_csv(tmp/'bad_ass.csv',ass,list(rows[0]))
            expect_error(lambda:analyze(tmp/'bad_ass.csv',tmp/'score.csv',tmp/'results',2,5,5),'pair')
            return
        elif test=='equal_scores_zero_effect':
            pass
        score_path=tmp/'score.csv';write_csv(score_path,score_rows,['run_id','score'])
        if test=='equal_scores_zero_effect':
            result=analyze(ap,score_path,tmp/'out',replicas=2,n_boot=100,n_perm=200)
            assert result['paired_delta_AB_minus_BASELINE']==0
            assert result['paired_signflip_two_sided_p']==1
            assert result['cluster_bootstrap_95_CI']==[0,0]
        elif test=='missing_grading':expect_error(lambda:analyze(ap,score_path,tmp/'out',2,5,5),'Incomplete')
        elif test=='duplicate_grading':expect_error(lambda:analyze(ap,score_path,tmp/'out',2,5,5),'Duplicate')
        elif test=='invalid_score':expect_error(lambda:analyze(ap,score_path,tmp/'out',2,5,5))

start=time.perf_counter()
results=[]
for name,expectation in CASES:
    for i in range(5):
        started=time.perf_counter()
        try:
            with tempfile.TemporaryDirectory() as td:
                check(name,i,Path(td))
            status='PASS';error=''
        except Exception as exc:
            status='FAIL';error=f'{type(exc).__name__}: {exc}'
        results.append({'case_id':f'INFRA-{len(results)+1:02}', 'test_family':name,'variant':i+1,'expected':expectation,
                        'status':status,'duration_ms':round((time.perf_counter()-started)*1000,3), 'error':error})
summary={'date':'2026-10-21','scope':'INFRASTRUCTURE_ONLY','n_scenarios':len(results),'n_passed':sum(r['status']=='PASS' for r in results),
         'n_failed':sum(r['status']=='FAIL' for r in results),'total_wall_seconds':round(time.perf_counter()-start,4),
         'scientific_agent_trajectories':0,'bixbench_tasks_solved':0,
         'warning':'Not independent LLM trajectories; not evidence of AB advantage; exploratory infrastructure checks.'}
write_csv(OUT/'ledger_50.csv',results,['case_id','test_family','variant','expected','status','duration_ms','error'])
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(summary,indent=2,ensure_ascii=False))
if summary['n_failed']:print('FAILURES:',*[f"{r['case_id']}: {r['error']}" for r in results if r['status']=='FAIL'],sep='\n')
sys.exit(int(summary['n_failed']!=0))
