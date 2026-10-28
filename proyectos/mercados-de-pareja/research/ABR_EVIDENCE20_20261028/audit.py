"""AB-R EVIDENCE20 N23/N24. Synthetic and exact mathematical controls, no human data.
PREREG: 8949077025a8d585fecdc3cec09ec13710cd5a72
"""
import itertools, csv, json
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parent
SEEDS=[411,733,1099,1481,2017]

def blocking_count(partners):
    """Men 0..n-1 and women 0..n-1 share strict rank order (lower index preferred)."""
    n=len(partners); inverse=np.empty(n,dtype=int)
    for i,w in enumerate(partners): inverse[w]=i
    return sum(j < int(partners[i]) and i < int(inverse[j]) for i in range(n) for j in range(n))

checks=[]
for n in range(2,7):
    stable=[]
    for p in itertools.permutations(range(n)):
        if blocking_count(p)==0: stable.append(p)
    checks.append(dict(n=n,permutations=int(np.math.factorial(n)) if hasattr(np,'math') else int(__import__('math').factorial(n)),stable_count=len(stable),stable_assignment=' '.join(map(str,stable[0])) if stable else ''))
    assert stable==[tuple(range(n))],(n,stable)

rows=[]
means=np.array([.15,.35,.65,.85]); sigma=.08; n_per=6000
for seed in SEEDS:
    rng=np.random.default_rng(seed)
    labels=np.repeat(np.arange(4),n_per)
    x=np.clip(np.repeat(means,n_per)+rng.normal(0,sigma,len(labels)),0,1)
    y=np.clip(np.repeat(means,n_per)+rng.normal(0,sigma,len(labels)),0,1)
    # Independent attributes and random matching WITHIN group: zero structural within group covariance.
    def correlation(a,b): return float(np.corrcoef(a,b)[0,1])
    pooled=correlation(x,y)
    within=[correlation(x[labels==g],y[labels==g]) for g in range(4)]
    wperm=np.arange(len(x))
    for g in range(4):
        ids=np.where(labels==g)[0];wperm[ids]=rng.permutation(ids)
    spooled=correlation(x,y[wperm])
    global_perm=correlation(x,y[rng.permutation(len(x))])
    # Cov decomposition: pooled centered covariance equals average within-group plus covariance of group means.
    covtot=float(np.mean((x-x.mean())*(y-y.mean())))
    withincov=sum(float(np.mean((x[labels==g]-x[labels==g].mean())*(y[labels==g]-y[labels==g].mean()))) for g in range(4))/4
    betweencov=float(np.mean((np.array([x[labels==g].mean() for g in range(4)])-x.mean())*(np.array([y[labels==g].mean() for g in range(4)])-y.mean())))
    assert abs(covtot-withincov-betweencov)<1e-12
    rows.append(dict(seed=seed,n_pairs=len(x),r_pooled=pooled,r_within_mean=float(np.mean(within)),r_stratified_permutation=spooled,r_global_permutation=global_perm,total_covariance=covtot,within_covariance=withincov,between_covariance=betweencov,share_between=betweencov/covtot))

with open(OUT/'EXACT_ENUMERATION.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
with open(OUT/'SEGMENT_NULLS.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'n23':checks,'n24':{k:float(np.mean([r[k] for r in rows])) for k in rows[0] if k not in ('seed','n_pairs')},'seeds':SEEDS,'external_replication':False}
(OUT/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,indent=2))
