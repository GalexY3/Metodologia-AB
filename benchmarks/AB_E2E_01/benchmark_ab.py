#!/usr/bin/env python3
"""Paired, cluster-aware AB-versus-competent-baseline research benchmark.

No model API calls, no benchmark answers, and no implicit scoring are provided.
The scorer is external and must remain blind to the experimental condition.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

ARMS = ('AB', 'BASELINE')
FIELDS = ['run_id', 'task_id', 'cluster_id', 'benchmark', 'replica', 'arm', 'order_key']

def digest(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def read_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def prepare(inventory, output, seed, n_clusters, replicas, benchmark):
    if replicas < 1 or n_clusters < 1: raise ValueError('n_clusters and replicas must be positive')
    tasks=read_csv(inventory)
    for required in ('task_id','cluster_id','benchmark'):
        if not tasks or required not in tasks[0]: raise ValueError(f'Inventory missing {required}')
    seen=set();by_cluster=defaultdict(list)
    for t in tasks:
        if not all(t[k].strip() for k in ('task_id','cluster_id','benchmark')): raise ValueError('Blank identifier')
        if t['task_id'] in seen: raise ValueError('Duplicate task_id')
        seen.add(t['task_id'])
        if t['benchmark']==benchmark: by_cluster[t['cluster_id']].append(t)
    clusters=sorted(by_cluster, key=lambda x:digest(seed+'|cluster|'+x))
    if len(clusters)<n_clusters: raise ValueError(f'Need {n_clusters} independent clusters; found {len(clusters)}')
    selected=[]
    for cl in clusters[:n_clusters]:
        selected.append(min(by_cluster[cl], key=lambda t:digest(seed+'|task|'+t['task_id'])))
    rows=[]
    for t in selected:
        for rep in range(1,replicas+1):
            for arm in ARMS:
                key=f'{seed}|{t["task_id"]}|{rep}|{arm}'
                rows.append(dict(run_id=digest('run|'+key)[:20],task_id=t['task_id'],
                    cluster_id=t['cluster_id'],benchmark=benchmark,replica=rep,
                    arm=arm,order_key=digest('order|'+key)[:20]))
    rows.sort(key=lambda x:x['order_key'])
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'assignments_RESTRICTED.csv',rows,FIELDS)
    write_csv(out/'grader_manifest_BLIND.csv',rows,['run_id','task_id','cluster_id','benchmark','replica'])
    (out/'SELECTION_MANIFEST.json').write_text(json.dumps({
        'seed':seed,'benchmark':benchmark,'n_clusters':n_clusters,'replicas':replicas,
        'inventory_sha256':hashlib.sha256(Path(inventory).read_bytes()).hexdigest(),
        'selected_task_ids':sorted(t['task_id'] for t in selected),
        'selected_clusters':sorted(t['cluster_id'] for t in selected),
        'run_count':len(rows)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'clusters':n_clusters,'runs':len(rows),'output':str(out)},ensure_ascii=False))

def validate_assignments(rows,replicas):
    if not rows:raise ValueError('No runs')
    ids=[x['run_id'] for x in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate run_id')
    pair=defaultdict(set); per_cluster=defaultdict(set)
    for r in rows:
        if r['arm'] not in ARMS:raise ValueError('Unknown arm')
        pair[(r['cluster_id'],r['task_id'],r['replica'])].add(r['arm'])
        per_cluster[r['cluster_id']].add(r['task_id'])
    if any(arms!=set(ARMS) for arms in pair.values()):raise ValueError('Incomplete AB/BASELINE pair')
    if any(len(tasks)!=1 for tasks in per_cluster.values()):raise ValueError('More than one task per cluster')
    if any(len([p for p in pair if p[0]==cl])!=replicas for cl in per_cluster):raise ValueError('Replica mismatch')
    return len(per_cluster)

def blinded(submissions,assignments,output):
    runs=read_csv(assignments); validate_assignments(runs, len({r['replica'] for r in runs}))
    ids={r['run_id'] for r in runs}
    data=read_csv(submissions)
    if not data or not {'run_id','answer'}.issubset(data[0]):raise ValueError('submissions must have run_id,answer')
    if len(data)!=len({r['run_id'] for r in data}):raise ValueError('Duplicate submission')
    if not {r['run_id'] for r in data}.issubset(ids):raise ValueError('Unknown run_id')
    # Deliberately never expose condition or internal budget fields to grader.
    write_csv(output,[{'run_id':r['run_id'],'answer':r['answer']} for r in data],['run_id','answer'])

def analyze(assignments,scores,output,replicas=2,n_boot=20000,n_perm=100000,seed=20261021):
    rows=read_csv(assignments);n_clusters=validate_assignments(rows,replicas)
    scored=read_csv(scores)
    if not scored or not {'run_id','score'}.issubset(scored[0]):raise ValueError('scores must have run_id,score')
    scores_by_id={}
    for r in scored:
        if r['run_id'] in scores_by_id:raise ValueError('Duplicate graded run')
        v=float(r['score'])
        if not np.isfinite(v) or not 0<=v<=1:raise ValueError('Score outside [0,1]')
        scores_by_id[r['run_id']]=v
    if set(scores_by_id)!={r['run_id'] for r in rows}:
        raise ValueError('Incomplete grading. Do not silently replace ungraded runs with zeros; explicitly grade timeouts/refusals as 0.')
    d=defaultdict(lambda:defaultdict(list))
    for r in rows:d[r['cluster_id']][r['arm']].append(scores_by_id[r['run_id']])
    by_cluster=[]
    for cl,arms in sorted(d.items()):
        if any(len(arms[a])!=replicas for a in ARMS):raise ValueError('Arm/replica count mismatch')
        ab=float(np.mean(arms['AB']));base=float(np.mean(arms['BASELINE']))
        by_cluster.append({'cluster_id':cl,'AB':ab,'BASELINE':base,'delta':ab-base})
    diff=np.array([x['delta'] for x in by_cluster]);obs=float(diff.mean())
    rng=np.random.default_rng(seed)
    ix=rng.integers(0,n_clusters,size=(n_boot,n_clusters))
    boot=diff[ix].mean(axis=1)
    ci=np.quantile(boot,[.025,.975]).tolist()
    # Sign-flip randomization inference: paired exchangeability under sharp null.
    hits=0;total=0;batch=10000
    for _ in range(0,n_perm,batch):
        size=min(batch,n_perm-total)
        signs=rng.choice([-1,1],size=(size,n_clusters))
        means=(signs*diff).mean(axis=1)
        hits+=int(np.count_nonzero(np.abs(means)>=abs(obs)-1e-12))
        total+=size
    p=(hits+1)/(total+1)
    summary={'status':'EVALUATED','benchmark':rows[0]['benchmark'],'n_clusters':n_clusters,
        'replicas_per_arm':replicas,'n_runs':len(rows),'mean_AB':float(np.mean([r['AB'] for r in by_cluster])),
        'mean_BASELINE':float(np.mean([r['BASELINE'] for r in by_cluster])),
        'paired_delta_AB_minus_BASELINE':obs,'cluster_bootstrap_95_CI':ci,
        'paired_signflip_two_sided_p':float(p),'bootstrap_replicates':n_boot,
        'permutation_replicates':total,
        'predefined_superiority_gate':bool(ci[0]>0 and p<.05),
        'caveat':'Grader validity, model isolation, data contamination and budgets require independent audit; this analysis alone cannot validate those assumptions.'}
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'cluster_results.csv',by_cluster,['cluster_id','AB','BASELINE','delta'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('prepare');a.add_argument('--inventory',required=True);a.add_argument('--out',required=True)
    a.add_argument('--seed',default='AB-E2E-20261021-LOCKED-01');a.add_argument('--clusters',type=int,default=60)
    a.add_argument('--replicas',type=int,default=2);a.add_argument('--benchmark',default='BixBench')
    b=sub.add_parser('blind');b.add_argument('--submissions',required=True);b.add_argument('--assignments',required=True);b.add_argument('--out',required=True)
    c=sub.add_parser('analyze');c.add_argument('--assignments',required=True);c.add_argument('--scores',required=True)
    c.add_argument('--out',required=True);c.add_argument('--replicas',type=int,default=2)
    c.add_argument('--bootstrap',type=int,default=20000);c.add_argument('--permutations',type=int,default=100000)
    args=p.parse_args()
    if args.cmd=='prepare':prepare(args.inventory,args.out,args.seed,args.clusters,args.replicas,args.benchmark)
    elif args.cmd=='blind':blinded(args.submissions,args.assignments,args.out)
    else:analyze(args.assignments,args.scores,args.out,args.replicas,args.bootstrap,args.permutations)
if __name__=='__main__':main()
