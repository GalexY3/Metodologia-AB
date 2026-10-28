"""EVIDENCE6: Synthetic methodological controls, NOT human estimates.
Frozen rule specification: PREREG.json commit 4c8cf495326d28faa8ae3ccb42c0b99469655e6c.
"""
import json, csv, hashlib
from pathlib import Path
import numpy as np
OUT=Path(__file__).parent
SEEDS=[1103,2207,3301,4409,5501]

def graph_and_vals(seed, n=120, k=20):
    rng=np.random.default_rng(seed)
    sm,bm,sw,bw=(rng.random(n) for _ in range(4))
    vm=.6*sm+.4*bm; vw=.4*sw+.6*bw
    # Regular bipartite graph: one edge per modular cyclic shift, with randomized labels
    pm=rng.permutation(n); pw=rng.permutation(n)
    shifts=rng.choice(n,size=k,replace=False)
    edges=[(int(pm[j]),int(pw[(j+int(shift))%n])) for shift in shifts for j in range(n)]
    rng.shuffle(edges)
    # Fixed dyadic utilities; each endpoint values other, plus fixed personal taste
    um=np.full((n,n),-np.inf); uw=np.full((n,n),-np.inf)
    for m,w in edges:
        um[m,w]=float(np.clip(vw[w]+rng.normal(0,.05),0,1))
        uw[m,w]=float(np.clip(vm[m]+rng.normal(0,.05),0,1))
    return rng,edges,um,uw,vm,vw

def DA(n,edges,um,uw, outside=.05):
    opts=[[] for _ in range(n)]
    for m,w in edges:
        if um[m,w]>=outside and uw[m,w]>=outside: opts[m].append(w)
    for m in range(n):opts[m].sort(key=lambda w:um[m,w],reverse=True)
    c=[0]*n; pm=np.full(n,-1,int); pw=np.full(n,-1,int)
    queue=list(range(n)); head=0
    while head<len(queue):
        m=queue[head];head+=1
        while c[m]<len(opts[m]) and pm[m]<0:
            w=opts[m][c[m]];c[m]+=1
            old=pw[w]
            if old<0 or uw[m,w]>uw[old,w]:
                if old>=0:
                    pm[old]=-1;queue.append(int(old))
                pm[m]=w;pw[w]=m
    return pm

def online(n,edges,um,uw,mode):
    pm=np.full(n,-1,int);pw=np.full(n,-1,int)
    qm=np.full(n,.8);qw=np.full(n,.8)
    for m,w in edges:
        if pm[m]>=0 or pw[w]>=0:continue
        a=um[m,w]>= (.05 if mode=='greedy' else qm[m]);b=uw[m,w]>= (.05 if mode=='greedy' else qw[w]);
        if a and b:pm[m]=w;pw[w]=m
        elif mode=='adaptive':
            qm[m]=max(.05,qm[m]-.02);qw[w]=max(.05,qw[w]-.02)
    return pm

def assess(pm,edges,um,uw,vm,vw):
    n=len(pm);m=np.flatnonzero(pm>=0);w=pm[m]
    if len(m)<4: raise ValueError('low number of matches')
    r=float(np.corrcoef(vm[m],vw[w])[0,1]);gap=float(np.median(abs(vm[m]-vw[w])))
    currentW=np.full(n,-1,int);currentW[w]=m
    block=0
    for a,b in edges:
        if pm[a]==b or um[a,b]<.05 or uw[a,b]<.05:continue
        ma=pm[a];wb=currentW[b]
        if (ma<0 or um[a,b]>um[a,ma]) and (wb<0 or uw[a,b]>uw[wb,b]):block+=1
    return dict(pairs=int(len(m)),coverage=2*len(m)/(2*n),r=r,gap=gap,blocking_pairs=block,average_utility=float((um[m,w]+uw[m,w]).mean()/2))

def evaluate_matching_from_likes(n,edges,um,uw,likeM,likeW):
    candidates=[(m,w) for m,w in edges if likeM[m,w] and likeW[m,w]]
    candidates.sort(key=lambda e:float(um[e]+uw[e]),reverse=True)
    pm=np.full(n,-1,int);usedW=np.zeros(n,bool)
    for m,w in candidates:
        if pm[m]<0 and not usedW[w]:pm[m]=w;usedW[w]=True
    return pm,len(candidates)

def process_views(n,edges,um,uw,kind,qkind):
    # Everybody evaluates their same k incoming candidate edges exactly once.
    # Match formation is DELAYED until all views are completed; hence no exit changes the candidate set.
    # Static negative control: order must not affect mutual likes when no expiration.
    # 'clock' indexes planned individual side-evaluations, not calendar days.
    likeM=np.zeros((n,n),bool);likeW=np.zeros((n,n),bool)
    seenM=np.full((n,n),-1,int);seenW=np.full((n,n),-1,int)
    qM=np.full(n,.75);qW=np.full(n,.75)
    if kind=='sync':
        jobs=[(m,w,0) for m,w in edges]+[(m,w,1) for m,w in edges]
        # make each edge's 2 views consecutive
        jobs=[(m,w,side) for m,w in edges for side in [0,1]]
    else:
        # same directed edge set, opposite viewing schedule of side 1.
        jobs=[(m,w,0) for m,w in edges]+[(m,w,1) for m,w in edges[::-1]]
    countM=np.zeros(n,int);countW=np.zeros(n,int)
    for t,(m,w,side) in enumerate(jobs):
        if side==0:
            a=um[m,w]>=qM[m];likeM[m,w]=a;seenM[m,w]=countM[m];countM[m]+=1
            if qkind=='adaptive' and not a:qM[m]=max(.05,qM[m]-.008)
        else:
            a=uw[m,w]>=qW[w];likeW[m,w]=a;seenW[m,w]=countW[w];countW[w]+=1
            if qkind=='adaptive' and not a:qW[w]=max(.05,qW[w]-.008)
    effective=likeM&likeW
    if kind=='async_expire5':
        # five rounds in rank of candidate evaluations per side, not absolute global time.
        # Each side's candidate encounter order index is computed from view count at own side.
        # Alternative operationalisation of TTL: 5% of scheduled edge count, declared before testing.
        threshold=5
        effective &= (np.abs(seenM-seenW)<=threshold)
    pm,candidates=evaluate_matching_from_likes(n,edges,um,uw,likeM,effective)
    return pm,dict(right_m=int(likeM.sum()),right_w=int(likeW.sum()),mutual_likes=candidates,directed_exposures=len(jobs),potential_edges=len(edges))

def run():
    rows=[]
    for seed in SEEDS:
        rng,edges,um,uw,vm,vw=graph_and_vals(seed)
        for mode in ['DA','greedy','adaptive']:
            pm=DA(len(vm),edges,um,uw) if mode=='DA' else online(len(vm),edges,um,uw,mode)
            a=assess(pm,edges,um,uw,vm,vw)
            if mode=='DA': assert a['blocking_pairs']==0
            rows.append(dict(cycle='N17',seed=seed,variant=mode,**a))
        for qkind in ['static','adaptive']:
            for kind in ['sync','async_persist','async_expire5']:
                pm,details=process_views(len(vm),edges,um,uw,kind,qkind)
                a=assess(pm,edges,um,uw,vm,vw)
                rows.append(dict(cycle='N18',seed=seed,variant=f'{qkind}_{kind}',**a,**details))
        # negative control invariant: with fixed q, same graph, no TTL, same mutual likes and match.
        sub=[r for r in rows if r['seed']==seed and r['cycle']=='N18']
        x={r['variant']:r for r in sub}
        for col in ['pairs','r','gap','mutual_likes']:
            assert x['static_sync'][col]==x['static_async_persist'][col],(seed,col)
    path=OUT/'RUNS.csv'
    with path.open('w',newline='') as f:
        cols=list(dict.fromkeys(key for row in rows for key in row.keys()))
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();writer.writerows(rows)
    (OUT/'QA.json').write_text(json.dumps({'seeds':SEEDS,'runs':len(rows),'DA_no_blocking':True,'N18_static_invariant':True,'N18_same_edges_all':True,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
    return rows
if __name__=='__main__':
    res=run()
    for key in sorted({(x['cycle'],x['variant']) for x in res}):
        a=[x for x in res if (x['cycle'],x['variant'])==key]
        print(key,'r',round(np.mean([q['r'] for q in a]),4),'coverage',round(np.mean([q['coverage'] for q in a]),4),'matches',round(np.mean([q['pairs'] for q in a]),1))
