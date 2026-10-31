"""Independent Python NetworkX exact integer and small exhaustive matching oracle.

Checks TS witness INDEPENDENTLY against primal-dual inequalities.
"""
import functools
import hashlib
import json
import math
from pathlib import Path
import networkx as nx

ROOT=Path(__file__).resolve().parent.parent
SCALE=2**52

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def small_dp(n,edges):
    adj=[{} for _ in range(n)]
    for a,b,res in edges:
        adj[a][b]=res;adj[b][a]=res
    @functools.cache
    def solve(mask):
        if not mask:return (0,0,1)
        v=(mask&-mask).bit_length()-1
        options=[solve(mask&~(1<<v))]
        for w,res in adj[v].items():
            if mask&(1<<w):
                card,wt,count=solve(mask&~(1<<v)&~(1<<w))
                options.append((card+1,wt+res,count))
        best=max((card,wt) for card,wt,_ in options)
        return (*best,sum(c for card,wt,c in options if (card,wt)==best))
    return solve((1<<n)-1)

def verify_primal_dual(row,input_edges):
    # This verifier has its OWN graph-to-dual math and does not invoke JS verifier.
    ans=row['outcome'];witness=ans['dual_witness'];n=witness['n']
    parent=witness['parent'];dual=witness['dual'];base=witness['base'];childs=witness['childs']
    p={}
    for a,b in ans['pairs']:
        assert a not in p and b not in p and a!=b
        p[a]=b;p[b]=a
    rdict={(a,b):int((w-1)*SCALE) for a,b,w in input_edges}
    fixed=ans['baseline_integer']
    wdict={k:v+fixed for k,v in rdict.items()}
    @functools.cache(None)
    def leaves(x):
        return (x,) if x<n else tuple(v for c in childs[x] for v in leaves(c))
    active=[]
    for b in range(n,2*n):
        if base[b]<0:continue
        assert dual[b]>=0 and isinstance(dual[b],int)
        ls=leaves(b)
        assert len(ls)%2==1 and len(ls)>=3 and len(ls)==len(set(ls))
        members=set(ls)
        matches=sum(1 for v in ls if v in p and p[v] in members and v<p[v])
        if dual[b]>0:assert matches==len(ls)//2
        active.append((b,ls))
    @functools.cache(None)
    def ancestors(v):
        ancestors=[];b=parent[v]
        while b>=0:
            assert n<=b<2*n and b not in ancestors
            ancestors.append(b);b=parent[b]
        return set(ancestors)
    assert all(x>=0 and isinstance(x,int) for x in dual)
    for v in range(n):
        if v not in p:assert dual[v]==0
    minslack=None
    for (a,b),weight in wdict.items():
        s=dual[a]+dual[b]-2*weight
        s+=2*sum(dual[bl] for bl,_ in active if bl in ancestors(a) and bl in ancestors(b))
        assert s>=0,(row['name'],'negative_slack',a,b,s)
        if p.get(a)==b:assert s==0,(row['name'],'non_tight_match',a,b,s)
        minslack=s if minslack is None else min(minslack,s)
    twice_dual=sum(dual[:n])+2*sum(dual[b]*(len(ls)//2) for b,ls in active)
    twice_primal=2*sum(wdict[tuple(sorted((a,b)))] for a,b in ans['pairs'])
    assert twice_dual==twice_primal,(row['name'],'dual_gap',twice_dual-twice_primal)
    assert twice_primal==ans['certificate']['objective2']
    return {'independent_dual_verified':True,'dual_objective2':twice_dual,'minslack2':minslack}

def main():
    source=ROOT/'GRAPH_INPUTS_N339.json'
    ts=ROOT/'outcomes'/'N339_POLY_GRAPHS.json'
    dest=ROOT/'outcomes'/'N339_INDEPENDENT_ORACLES.json'
    if dest.exists():raise SystemExit('NO_OVERWRITE')
    i=json.loads(source.read_text(encoding='utf8'))['cases']
    o=json.loads(ts.read_text(encoding='utf8'))['rows']
    assert len(i)==len(o)==12
    rows=[]
    for sourcecase,tscase in zip(i,o):
        assert sourcecase['name']==tscase['name']
        n=sourcecase['n'];edges=sourcecase['edges']
        G=nx.Graph();G.add_nodes_from(range(n))
        vals=[(a,b,int((w-1)*SCALE)) for a,b,w in edges]
        G.add_weighted_edges_from(vals)
        m=nx.max_weight_matching(G,maxcardinality=True,weight='weight')
        canonical=sorted(tuple(sorted(t)) for t in m)
        rdict={(a,b):v for a,b,v in vals}
        nx_res=sum(rdict[e] for e in canonical)
        ref={'cardinality':len(m),'residue':nx_res,'pairs':canonical}
        row={'name':sourcecase['name'],'status':tscase['status'],'networkx_integer':ref}
        if tscase['status']=='EXECUTED':
            ans=tscase['outcome']
            row['primal_dual']=verify_primal_dual(tscase,edges)
            row['objective_equal']=ans['cardinality']==len(m) and ans['exact_weight_residue']==nx_res
            row['pairs_identical']=ans['pairs']==[list(p) for p in canonical]
            assert row['objective_equal'],('MISMATCH',sourcecase['name'])
        if n<=14:
            card,res,count=small_dp(n,vals)
            row['dp']={'cardinality':card,'residue':res,'number_of_optimal_matchings':count}
            assert (card,res)==(ref['cardinality'],ref['residue'])
            if tscase['status']=='EXECUTED':
                assert (card,res)==(tscase['outcome']['cardinality'],tscase['outcome']['exact_weight_residue'])
        rows.append(row)
    report={'schema':'ABH_N339_INDEPENDENT_ORACLE_RESULT',
       'graph_inputs_sha256':sha(source),'ts_results_sha256':sha(ts),'cases':rows,
       'ts_completed':sum(x['status']=='EXECUTED' for x in rows),
       'ts_objective_equal_NX':sum(x.get('objective_equal',False) for x in rows),
       'independent_dual_certificates':sum(bool(x.get('primal_dual')) for x in rows),
       'dp_checked':sum('dp' in x for x in rows),
       'technical_only':True,'CT2':7,'STOP_R5_human':True}
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N339_INDEPENDENT_ORACLES',report['ts_completed'],
          report['ts_objective_equal_NX'],report['independent_dual_certificates'],
          report['dp_checked'],sha(dest))

if __name__=='__main__':main()
