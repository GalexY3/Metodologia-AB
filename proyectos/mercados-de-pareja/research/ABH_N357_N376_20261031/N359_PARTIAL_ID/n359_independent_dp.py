"""AB-H N359 independent exact-state DP oracle; no original human records."""
from pathlib import Path
import hashlib,json
from collections import defaultdict
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'outcomes'/'N359_PARTIAL_ID_SYNTHETIC.json'
DEST=ROOT/'outcomes'/'N359_PYTHON_DP_ORACLE.json'
assert SRC.exists() and not DEST.exists()
x=json.loads(SRC.read_text('utf8'))
assert x['schema']=='ABH_N359_SHARP_IDENTIFICATION_BOUNDS_V1' and len(x['rows'])==504
def exact_dp(graph,n):
    """Subset DP independent of JS augmenting-path algorithm."""
    masks={0}
    for i in range(n):
        later=set(masks)
        for mask in masks:
            for j in range(n):
                if graph[i*n+j] and not (mask>>j)&1:
                    later.add(mask|(1<<j))
        masks=later
    return max((k.bit_count() for k in masks),default=0)
audits=[]
for row in x['rows']:
    n=row['n'];obs=row['observed'];f=row['f_choice'];m=row['m_choice']
    assert n==9 and len(obs)==len(f)==len(m)==n*n
    assert all(v in (0,1) for arr in (obs,f,m) for v in arr)
    actual=[int(a and b) for a,b in zip(f,m)]
    low=[int(v and o) for v,o in zip(actual,obs)]
    high=[int(v or (not o)) for v,o in zip(actual,obs)]
    L,U,K=exact_dp(low,n),exact_dp(high,n),exact_dp(actual,n)
    assert (L,U,K)==(row['L'],row['U'],row['K']),row['seed']
    assert 0<=L<=K<=U<=n
    assert row['width']==U-L
    assert row['observed_pairs']==sum(obs)
    assert row['observed_mutual']==sum(low)
    if row['rate']==1:assert L==U==K
    audits.append((row['mode'],row['rate'],row['seed'],L,U,K))
assert len({seed for _,_,seed,*_ in audits})==504
manual=x['manual_counterexample']
n=manual['n'];obs=manual['observed']
assert n==4 and sum(obs)==4
zero=[0]*16;all_hidden=[int(not v) for v in obs]
assert exact_dp(zero,4)==manual['completion_zero_matching']==0
assert exact_dp(all_hidden,4)==manual['completion_all_hidden_yes_matching']==4
# Two injected false claims must be detected by the exact independent DP.
assert manual['completion_zero_matching']+1 != exact_dp(zero,4)
assert manual['completion_all_hidden_yes_matching']-1 != exact_dp(all_hidden,4)
by_group=defaultdict(list)
for mode,rate,seed,L,U,K in audits:
    by_group[(mode,rate)].append(U-L)
agg=[]
for a in x['aggregates']:
    z=by_group[(a['mode'],a['rate'])]
    assert len(z)==a['n']
    assert abs(sum(z)/len(z)-a['meanWidth'])<1e-12
    assert z.count(0)==a['pointIdentified']
    agg.append({'mode':a['mode'],'rate':a['rate'],'n':len(z),
       'mean_width':sum(z)/len(z),'point_id_count':z.count(0)})
report={
 'schema':'ABH_N359_PYTHON_INDEPENDENT_DP_V1',
 'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'all_504_checked':True,'checked_markets':len(audits),'checked_groups':len(agg),
 'matches_for_L_U_K':len(audits),'full_obs_collapsed':sum(rate==1 for mode,rate,*_ in audits),
 'manual_sharp_witness_passed':True,'deliberate_wrong_bounds_rejected':2,
 'aggregates':agg,'human_validation':False,'CT2':7,'STOP_R5':True}
DEST.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print('N359_PYTHON_DP_OK',report['checked_markets'],report['full_obs_collapsed'],
      hashlib.sha256(DEST.read_bytes()).hexdigest())
