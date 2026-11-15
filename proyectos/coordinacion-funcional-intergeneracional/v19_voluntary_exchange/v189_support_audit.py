"""Posthoc information audit and certified controlled-support construction.

Bounds and characteristic graphs are elementary/known information constraints,
not claimed original discoveries. No new neural training in this script.
"""
from pathlib import Path
import itertools
import json
import numpy as np

BASE=Path(__file__).resolve().parent
OUT=BASE/'results/V189_SUPPORT_AUDIT'
P=31


def confusability(mask):
    counts=mask.astype(np.int64)@mask.astype(np.int64).T
    graph=counts>0
    np.fill_diagonal(graph,False)
    return graph


def constrained_bounds(dictionary,mask,train_correct=None):
    symbols=np.unique(dictionary)
    table=np.zeros((len(symbols),P),dtype=np.int64)
    sizes=np.zeros(len(symbols),dtype=np.int64)
    for i,symbol in enumerate(symbols):
        aa=np.flatnonzero(dictionary==symbol)
        table[i]=mask[aa].sum(axis=0);sizes[i]=len(aa)
    train_max=int((table>0).sum())
    independent_test_max=int((table<sizes[:,None]).sum())
    c=train_max if train_correct is None else train_correct
    conditional_test_max=min(independent_test_max,len(symbols)*P-c)
    return dict(active_symbols=len(symbols),maximum_train_correct=train_max,
                maximum_train_accuracy=train_max/int(mask.sum()),
                unconditional_test_accuracy_bound=independent_test_max/int((~mask).sum()),
                test_accuracy_bound_at_given_train_correct=conditional_test_max/int((~mask).sum()),
                given_train_correct=float(c))


def regular_swap(mask,seed,attempts=20000):
    rng=np.random.default_rng(seed)
    result=mask.copy()
    edges=np.argwhere(np.triu(result,1))
    for _ in range(attempts):
        i,j=rng.choice(len(edges),2,replace=False)
        a,b=edges[i];c,d=edges[j]
        if len({int(a),int(b),int(c),int(d)})<4:continue
        if rng.random()<.5:c,d=d,c
        if result[a,d] or result[c,b]:continue
        result[a,b]=result[b,a]=False;result[c,d]=result[d,c]=False
        result[a,d]=result[d,a]=True;result[c,b]=result[b,c]=True
        edges[i]=sorted((a,d));edges[j]=sorted((c,b))
    return result


def main():
    OUT.mkdir(exist_ok=False)
    source=BASE/'results/V188_PRIVATE_CONVENTIONS'
    checks=[];per_history=[]
    # The exact policy-mixture bound also checks the implementation of expected
    # accuracy. Weighted full accuracy cannot exceed sum_m max_a pi(m|a)/P.
    for path in sorted(source.glob('*/metrics_s*.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        for row in data['history']:
            achieved=(387*row['train_expected']+574*row['test_expected'])/(P*P)
            ceiling=row['bayes_bound_full_stochastic']
            residual=achieved-ceiling
            checks.append(dict(family=data['family'],seed=data['seed'],step=row['step'],residual=residual,
                               passed=residual<=1e-5))
        checkpoint=json.loads((source/data['family']/'progress.json').read_text(encoding='utf-8'))
        # Final greedy support ceiling with the actually achieved train accuracy.
        final=data['final'];k=final['protocol_symbols']
        per_history.append(dict(seed=data['seed'],family=data['family'],symbols=k,
                                train=final['train'],test=final['test'],
                                test_bound_given_train=min(final['bayes_bound_test_greedy'],
                                    (k*P-387*final['train'])/574)))
    assert len(checks)==9600 and all(c['passed'] for c in checks)
    # Low-confusability support: an undirected 12-regular cycle-neighborhood graph.
    low=np.zeros((P,P),dtype=bool)
    for a in range(P):
        for d in range(1,7):low[a,(a+d)%P]=low[a,(a-d)%P]=True
    permutation=np.random.default_rng(189000).permutation(P)
    dictionary_old=np.full(P,-1,dtype=np.int64)
    for a in range(15):dictionary_old[a]=dictionary_old[a+15]=a
    dictionary_old[30]=15
    low=low[np.ix_(permutation,permutation)]
    dictionary=dictionary_old[permutation]
    g_low=confusability(low)
    assert len(set(dictionary.tolist()))==16
    assert all(dictionary[a]!=dictionary[b] for a,b in np.argwhere(g_low))
    independent_triples=[triple for triple in itertools.combinations(range(P),3)
                         if all(not g_low[a,b] for a,b in itertools.combinations(triple,2))]
    assert not independent_triples # alpha<=2, hence chi>=ceil(31/2)=16
    high=None;selected_seed=None
    # Selection is by a prespecified graph property, never a learned outcome.
    for seed in range(189001,189101):
        candidate=regular_swap(low,seed)
        g=confusability(candidate)
        if np.sum(g)==P*(P-1):high=candidate;selected_seed=seed;break
    assert high is not None
    assert np.array_equal(low,low.T) and np.array_equal(high,high.T)
    assert np.all(low.sum(axis=0)==12) and np.all(high.sum(axis=0)==12)
    assert np.all(low.sum(axis=1)==12) and np.all(high.sum(axis=1)==12)
    assert low.sum()==high.sum()==372
    low_bounds=constrained_bounds(dictionary,low)
    assert low_bounds['maximum_train_accuracy']==1.
    assert low_bounds['test_accuracy_bound_at_given_train_correct']==124/589
    aa,bb=np.indices((P,P));yy=(aa+bb)%P
    np.savez_compressed(OUT/'matched_supports.npz',low=low,high=high,
                        low_oracle_dictionary=dictionary,permutation=permutation,a=aa.ravel(),b=bb.ravel(),y=yy.ravel())
    report=dict(posthoc_audit=True,no_new_neural_training=True,number_expected_accuracy_checks=len(checks),
                all_capacity_checks_passed=True,max_residual=max(c['residual'] for c in checks),
                final_history_bounds=per_history,
                controlled_supports=dict(P=P,train_pairs=372,test_pairs=589,
                    both_marginal_degrees=12,both_symmetric=True,low_chromatic_number=16,
                    low_upper_certificate='explicit 16-coloring',low_lower_certificate='no independent triple',
                    high_chromatic_number=31,high_certificate='complete confusability graph',
                    high_construction_seed=selected_seed,selection_uses_neural_outcomes=False,
                    low_oracle_bounds=low_bounds,oracle_dictionary_learned_by_agents=False),
                theoretical_scope='Known information/graph constraints; new controlled dataset, not an original theorem',
                CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (OUT/'capacity_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    (OUT/'SUMMARY.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='final_history_bounds'},indent=2),flush=True)


if __name__=='__main__':main()
