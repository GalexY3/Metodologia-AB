"""Smoke tests for the benchmark *infrastructure*, not evidence about AB."""
import csv, subprocess, sys, tempfile, pathlib, json
from benchmark_ab import prepare, analyze, blinded, read_csv, write_csv

def test_harness():
    with tempfile.TemporaryDirectory() as tmp:
        root=pathlib.Path(tmp)
        inv=root/'inventory.csv'
        write_csv(inv,[{'task_id':f'question_{i}','cluster_id':f'capsule_{i}', 'benchmark':'BixBench'} for i in range(8)],['task_id','cluster_id','benchmark'])
        prepare(inv,root/'run1','fixed',6,2,'BixBench')
        prepare(inv,root/'run2','fixed',6,2,'BixBench')
        p=root/'run1'/'assignments_RESTRICTED.csv';q=root/'run2'/'assignments_RESTRICTED.csv'
        assert p.read_bytes()==q.read_bytes(),'Non-deterministic run manifest'
        runs=read_csv(p); assert len(runs)==24
        assert len(set(r['cluster_id'] for r in runs))==6
        submissions=[{'run_id':r['run_id'],'answer':'synthetic-test-answer'} for r in runs]
        write_csv(root/'submissions.csv',submissions,['run_id','answer'])
        blinded(root/'submissions.csv',p,root/'blind.csv')
        assert 'arm' not in (root/'blind.csv').read_text()
        scores=[{'run_id':r['run_id'],'score':str(1 if r['arm']=='AB' else 0)} for r in runs]
        write_csv(root/'scores.csv',scores,['run_id','score'])
        summary=analyze(p,root/'scores.csv',root/'results',replicas=2,n_boot=1000,n_perm=5000)
        assert summary['paired_delta_AB_minus_BASELINE']==1
        assert summary['n_clusters']==6
        scores.pop()
        write_csv(root/'scores_incomplete.csv',scores,['run_id','score'])
        try:analyze(p,root/'scores_incomplete.csv',root/'invalid',replicas=2,n_boot=10,n_perm=10)
        except ValueError as e:assert 'Incomplete' in str(e)
        else:raise AssertionError('Incomplete grading silently accepted')
        print('TESTS PASSED: deterministic assignment, paired clusters, blinded grading, missingness fail-closed')

if __name__=='__main__':test_harness()
