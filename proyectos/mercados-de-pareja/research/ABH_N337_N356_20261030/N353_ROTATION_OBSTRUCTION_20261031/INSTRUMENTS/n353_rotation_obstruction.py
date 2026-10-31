"""N353: test structural conditions for distinct stable matchings.

Frozen actual synthetic accepted graphs (96) versus a separate, explicitly
counterfactual minimal four-actor preference cycle. This does NOT assert
unseen actor contacts occurred or observed real ordinal preferences.
"""
import hashlib,json,itertools
from pathlib import Path
import networkx as nx
from n351_da_central import da,blocking,canonical
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'N351_BIPARTITE_INPUTS.json'
SENS=ROOT/'outcomes'/'N352_PREFERENCE_HETEROGENEITY.json'
OUT=ROOT/'outcomes'/'N353_ROTATION_OBSTRUCTION.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def possible_matching_sets(W,M,edges):
    eligible=set(map(tuple,edges))
    def rec(ww):
        if not ww:
            yield ()
            return
        w=ww[0]
        yield from rec(ww[1:])
        for m in M:
            if (w,m) not in eligible:continue
            for rest in rec(ww[1:]):
                if any(y==m for _,y in rest):continue
                yield ((w,m),)+rest
    return [canonical(x) for x in rec(W)]
def main():
    if OUT.exists():raise SystemExit('NO_OVERWRITE')
    assert sha(SOURCE)=='42c24b43bde724d0609d816a57f6287c17c0f201705382031d8f00cecfe28d35'
    assert sha(SENS)=='5907663ba2e24ccc5122f19f176e7f07c82804771bc68f62391c565d69871187'
    source=json.loads(SOURCE.read_text())['markets']
    sens=json.loads(SENS.read_text())['cases']
    report=[]
    for m in source:
        G=nx.Graph();G.add_nodes_from(m['women']+m['men']);G.add_edges_from(m['edges'])
        ranks=len(m['edges'])-G.number_of_nodes()+nx.number_connected_components(G)
        assert ranks>=0
        cycles=nx.cycle_basis(G)
        # Enumerate 4-cycle existence independently from cycle_basis.
        full=set(tuple(sorted(z)) for z in m['edges'])
        overlap=0
        woman_set=set(m['women'])
        oriented=[(a,b) if a in woman_set else (b,a) for a,b in m['edges']]
        for w1,w2 in itertools.combinations(m['women'],2):
            common={a for w,a in oriented if w==w1}&{a for w,a in oriented if w==w2}
            overlap+=len(common)*(len(common)-1)//2
        best=None
        # Two disjoint EXISTING pairs are enough to specify a candidate 2x2
        # intervention; O(E²), avoiding all W²*M² hypothetical quadruples.
        for (w1,a),(w2,bb) in itertools.combinations(oriented,2):
            if w1==w2 or a==bb:continue
            if w1>w2:
                w1,w2=w2,w1
                a,bb=bb,a
            if a>bb:a,bb=bb,a
            alternatives=[tuple(sorted(x)) for x in
                 [(w1,a),(w1,bb),(w2,a),(w2,bb)]]
            missing=sum(e not in full for e in alternatives)
            candidate=(missing,w1,w2,a,bb)
            if best is None or candidate<best:best=candidate
        # Evaluate all five fixed preference models: graph with no cycle
        # cannot have two distinct stable matchings on identical partner set.
        nested=[x for x in sens if x['seed']==m['seed'] and x['t']==m['t']]
        assert len(nested)==5
        different=sum(not x['same_da_pairs'] for x in nested)
        assert different==0  # log as newly tested graph-conditional rule
        synthetic=None
        if best is not None:
            missing,w1,w2,a,bb=best
            quad=[[w1,a],[w1,bb],[w2,a],[w2,bb]]
            # Crossed 2-sided preferences: F1 prefers M1, F2 prefers M2;
            # M1 prefers F2, M2 prefers F1. Each DA proposes to its ideal.
            prefs={str(w1):[a,bb],str(w2):[bb,a],
                   str(a):[w2,w1],str(bb):[w1,w2]}
            first=da([w1,w2],[a,bb],prefs)
            second=da([a,bb],[w1,w2],prefs)
            expected1=canonical([[w1,a],[w2,bb]])
            expected2=canonical([[w1,bb],[w2,a]])
            assert first==expected1 and second==expected2 and first!=second
            allstable=[x for x in possible_matching_sets([w1,w2],[a,bb],quad)
                       if len(blocking(x,quad,prefs))==0]
            assert sorted(allstable)==sorted([first,second])
            synthetic={'minimal_new_eligibility_edges_to_complete_4cycle':missing,
                       'added_edges_NOT_NATIVE':[e for e in quad if tuple(sorted(e)) not in full],
                       'baseline_existing_edge_count_in_quad':4-missing,
                       'female_proposing':first,'male_proposing':second,
                       'exact_stable_matching_count_by_brute_force':len(allstable),
                       'four_actor_counterfactual':True,
                       'synthetic_assumed_preference_lists':prefs}
        report.append({'seed':m['seed'],'t':m['t'],'native_eligible_edges':len(m['edges']),
            'cycle_space_dimension':ranks,'cycle_basis_size':len(cycles),
            'number_4cycles':overlap,'five_preference_models_proposer_diff':different,
            'minimal_four_actor_rotation_witness':synthetic})
    assert len(report)==96
    summ={'markets':96,'acyclic_markets':sum(x['cycle_space_dimension']==0 for x in report),
          'markets_with_any_cycle':sum(x['cycle_space_dimension']>0 for x in report),
          'markets_with_4cycle':sum(x['number_4cycles']>0 for x in report),
          'markets_admitting_two_disjoint_existing_pairs':sum(x['minimal_four_actor_rotation_witness'] is not None for x in report),
          'minimum_new_eligibility_edges_by_market':{}}
    for z in report:
        w=z['minimal_four_actor_rotation_witness']
        if w:
            k=str(w['minimal_new_eligibility_edges_to_complete_4cycle'])
            summ['minimum_new_eligibility_edges_by_market'][k]=summ['minimum_new_eligibility_edges_by_market'].get(k,0)+1
    result={'schema':'N353_SYNTHETIC_ACCEPTANCE_GRAPH_ROTATION_GATE',
      'original_market_SHA':sha(SOURCE),'pre_frozen_DA5_models_SHA':sha(SENS),
      'summary':summ,'cases':report,
      'theory':'Distinct stable matchings on same market imply an alternating even cycle; 4-actor 2x2 constructed as a minimal explicit hypothetical exposure intervention, not historical observed acceptance.',
      'CT2':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('N353_ROTATIONS',summ,'SHA',sha(OUT))
if __name__=='__main__':main()
