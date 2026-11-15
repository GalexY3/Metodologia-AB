"""Construct four context pairs matched on input and label marginals.

V189's first control matched inputs but not output-label frequencies. Preserve
that prototype; do not train on it as a clean graph contrast. Selection below
uses graph/statistical constraints only, never neural training outcomes.
"""
from pathlib import Path
import hashlib
import json
import itertools
import numpy as np
from numba import njit
from v189_support_audit import confusability,constrained_bounds
from research_resource_limits import apply_limits

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V189B_MATCHED_CONTEXTS'
P=31


@njit(cache=True)
def complete_confusability(matrix):
    for a in range(P):
        for b in range(a+1,P):
            found=False
            for k in range(P):
                if matrix[a,k] and matrix[b,k]:found=True;break
            if not found:return False
    return True


@njit(cache=True)
def label_counts(matrix):
    counts=np.zeros(P,dtype=np.int64)
    for a in range(P):
        for b in range(a+1,P):
            if matrix[a,b]:counts[(a+b)%P]+=1
    return counts


@njit(cache=True)
def search_control(initial,seed,iterations=1000000):
    np.random.seed(seed)
    matrix=initial.copy()
    edges=np.empty((186,2),dtype=np.int64);k=0
    for a in range(P):
        for b in range(a+1,P):
            if matrix[a,b]:edges[k,0]=a;edges[k,1]=b;k+=1
    assert k==186
    target=label_counts(matrix);current=target.copy();score=0
    for step in range(iterations):
        i=np.random.randint(len(edges));j=np.random.randint(len(edges))
        if i==j:continue
        a,b=edges[i];c,d=edges[j]
        if a==c or a==d or b==c or b==d:continue
        if np.random.random()<.5:c,d=d,c
        if matrix[a,d] or matrix[c,b]:continue
        candidate=current.copy()
        candidate[(a+b)%P]-=1;candidate[(c+d)%P]-=1
        candidate[(a+d)%P]+=1;candidate[(c+b)%P]+=1
        new_score=np.sum((candidate-target)**2)
        phase=(step%20000)/20000.
        temperature=max(.025,2.*(1.-phase)**3)
        if new_score>score and np.random.random()>=np.exp((score-new_score)/temperature):continue
        matrix[a,b]=matrix[b,a]=False;matrix[c,d]=matrix[d,c]=False
        matrix[a,d]=matrix[d,a]=True;matrix[c,b]=matrix[b,c]=True
        edges[i,0]=a;edges[i,1]=d;edges[j,0]=c;edges[j,1]=b
        current=candidate;score=new_score
        if step>=1000 and score==0 and complete_confusability(matrix):
            return matrix,step+1,True
    return matrix,iterations,False


def main():
    OUT.mkdir(exist_ok=False)
    raw=np.zeros((P,P),dtype=bool)
    for a in range(P):
        for d in range(1,7):raw[a,(a+d)%P]=raw[a,(a-d)%P]=True
    old_dictionary=np.full(P,-1,dtype=np.int64)
    for a in range(15):old_dictionary[a]=old_dictionary[a+15]=a
    old_dictionary[30]=15
    aa,bb=np.indices((P,P));yy=(aa+bb)%P
    summaries=[]
    for pair in range(4):
        permutation=np.random.default_rng(189000+pair).permutation(P)
        low=raw[np.ix_(permutation,permutation)]
        dictionary=old_dictionary[permutation]
        selected=None
        for seed in range(189100+pair*100,189200+pair*100):
            high,attempts,found=search_control(low,seed)
            if found:selected=seed;break
        assert selected is not None,'No matched complete-confusability control; do not silently loosen constraints'
        assert np.array_equal(low,low.T) and np.array_equal(high,high.T)
        assert np.all(low.sum(0)==12) and np.all(high.sum(0)==12)
        assert np.array_equal(label_counts(low),label_counts(high))
        assert np.min(label_counts(low))>0
        assert low.sum()==high.sum()==372
        glow=confusability(low);ghigh=confusability(high)
        assert np.sum(ghigh)==P*(P-1)
        assert all(dictionary[a]!=dictionary[b] for a,b in np.argwhere(glow))
        assert not any(all(not glow[a,b] for a,b in itertools.combinations(t,2))
                       for t in itertools.combinations(range(P),3))
        path=OUT/f'pair_{pair}.npz'
        np.savez_compressed(path,low=low,high=high,low_oracle_dictionary=dictionary,
                            a=aa.ravel(),b=bb.ravel(),y=yy.ravel())
        summary=dict(pair=pair,permutation_seed=189000+pair,control_seed=selected,proposals=attempts,
                     train_pairs=372,test_pairs=589,input_degrees=12,
                     all_input_and_output_marginals_match=True,output_train_counts=(2*label_counts(low)).tolist(),
                     low_chromatic=16,high_chromatic=31,low_oracle_bounds=constrained_bounds(dictionary,low),
                     data_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),neural_outcomes_used=False)
        summaries.append(summary);print('CONSTRUCTED',json.dumps(summary),flush=True)
    (OUT/'SUMMARY.json').write_text(json.dumps(dict(
        prototype_V189_label_marginals_not_matched=True,prototype_preserved=True,
        purpose='Matched-support testbed; no new theorem or emergent learned behavior claimed',pairs=summaries,
        neural_training_executed=False,CT2_historical=61,new_branch_score=None,N2=0,N3=0),indent=2),encoding='utf-8')


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True);main()
