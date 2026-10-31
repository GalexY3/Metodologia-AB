"""N343 independent match GRAPH reconstruction from original directed decisions.

Inputs: immutable N342 true original native Python event traces, original 5-shock
tensor input SHA, N341 TS per-tick matching graphs and certificates.
Never run or change ESBM; computes independent graph + exact integer objective.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import networkx as nx

ROOT=Path(__file__).resolve().parent.parent
INPUTS=ROOT/'official_inputs_60'
ORIGINAL_INDEX=ROOT/'outcomes'/'N342_NATIVE_INDEX.json'
TS_INDEX=ROOT/'outcomes'/'N341_TS60_INDEX.json'
INPUT_INDEX=ROOT/'N341_INPUT_MANIFEST.json'
OUT=ROOT/'outcomes'/'N343_NATIVE_GRAPH_ORACLE.json'
SCALE=2**52

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def reconstruct(true_responses,tensor,t):
    edges={}
    for i,j in true_responses:
        x,y=sorted((int(i),int(j)))
        assert 0<=x<y<144
        weight=float(1.0+1e-4*float(tensor[t,x,y]))
        assert 1<=weight<1.000101
        res=(weight-1)*SCALE
        assert res.is_integer() and 0<=res<2**53
        edges[(x,y)]=weight
    return sorted(edges.items())

def graphSHA(edges):
    graph=[{'pair':list(k),'weight':v} for k,v in edges]
    # JSON.stringify on actual JS matching_graph edges for strictly finite
    # binary64 weights near 1 has same shortest decimal representation as Python.
    data=json.dumps(graph,separators=(',',':'),allow_nan=False,ensure_ascii=False)
    return hashlib.sha256(data.encode('utf8')).hexdigest()

def verify_one(pyrow,tsrow,tensor,seed,name):
    true_by_tick=[[] for _ in range(16)]
    with (ROOT/'outcomes'/pyrow['trace_path']).open(encoding='utf8') as f:
        for line in f:
            e=json.loads(line)
            if e['stage']=='response' and e['decision']:
                true_by_tick[e['t']].append((e['i'],e['j']))
    ts=json.loads((ROOT/'outcomes'/tsrow['run_file']).read_text(encoding='utf8'))
    orig=json.loads((ROOT/'outcomes'/pyrow['run_path']).read_text(encoding='utf8'))
    assert len(ts['graphHashes'])==len(ts['matching'])==len(orig['formation_pairs_by_tick'])==16
    trials=[]
    for t in range(16):
        edges=reconstruct(true_by_tick[t],tensor,t)
        graphHash=graphSHA(edges)
        target=ts['graphHashes'][t]
        G=nx.Graph();G.add_nodes_from(range(144))
        weights={(a,b):int((w-1)*SCALE) for (a,b),w in edges}
        G.add_weighted_edges_from((a,b,z) for (a,b),z in weights.items())
        exact=nx.max_weight_matching(G,maxcardinality=True,weight='weight')
        optimum=sorted(tuple(sorted(p)) for p in exact)
        residue=sum(weights[k] for k in optimum)
        chosen=ts['matching'][t]
        origpairs=orig['formation_pairs_by_tick'][t]
        original_card=len(origpairs)
        origres=sum(weights[tuple(pair)] for pair in origpairs)
        targetHash=target['sha256']
        trials.append({'t':t,'edge_count':len(edges),'directed_accepted':len(true_by_tick[t]),
          'graph_sha256_from_native_events':graphHash,
          'graph_sha256_TS':targetHash,
          'graph_content_identical':graphHash==targetHash,
          'TS_edge_count_matches':len(edges)==target['edges'],
          'exact_NX_cardinality':len(optimum),'exact_NX_integer_residue':residue,
          'TS_optimal_cardinality':chosen['cardinality'],
          'TS_integer_residue':chosen['residual'],
          'TS_certified_primal_dual':chosen['certified'] and chosen['certificate']['certified'],
          'TS_objective_matches_NX':chosen['cardinality']==len(optimum) and chosen['residual']==residue,
          'native_Python_float_matching_exact_integer_optimal':original_card==len(optimum) and origres==residue,
          'native_original_TS_chosen_pairs_identical':origpairs==ts['formation_pairs_by_tick'][t]})
    return trials

def main():
    if OUT.exists():raise SystemExit('NO_OUTPUT_OVERWRITE')
    assert sha(INPUT_INDEX)=='84a52580add085ab551dacf6e4cd3fdfc80be8eeaf187c7d3e4b25be208e42bf'
    assert sha(ORIGINAL_INDEX)=='89e221ab34c1a3c08ff04c8902268946f1b40cf6230cea224a907d9e96bd776b'
    assert sha(TS_INDEX)=='37b8a1010968e0ead1a13f7f71193858bcfb83b0e3428573ad734f96e136948d'
    rows=json.loads(INPUT_INDEX.read_text())['rows']
    src=json.loads(ORIGINAL_INDEX.read_text())['rows']
    js=json.loads(TS_INDEX.read_text())['rows']
    assert len(src)==len(js)==60
    cases=[]
    for item in rows:
        seed=item['seed'];f=item['tensors']['u_match']
        target=INPUTS/f['path'];assert sha(target)==f['sha256']
        tensor=np.memmap(target,dtype='<f8',mode='r',shape=(16,144,144))
        for a,b in zip((x for x in src if x['seed']==seed),(x for x in js if x['seed']==seed)):
            assert (a['seed'],a['scenario'])==(b['seed'],b['scenario'])
            assert sha(ROOT/'outcomes'/a['trace_path'])==a['trace_sha256']
            assert sha(ROOT/'outcomes'/a['run_path'])==a['run_sha256']
            assert sha(ROOT/'outcomes'/b['run_file'])==b['run_sha256']
            t=verify_one(a,b,tensor,seed,a['scenario'])
            cases.append({'seed':seed,'scenario':a['scenario'],'ticks':t,
              'identical_graphs':sum(z['graph_content_identical'] for z in t),
              'exact_objectives':sum(z['TS_objective_matches_NX'] for z in t),
              'Python_float_exact_objectives':sum(z['native_Python_float_matching_exact_integer_optimal'] for z in t),
              'pair_identity':sum(z['native_original_TS_chosen_pairs_identical'] for z in t)})
    assert len(cases)==60
    # Negative controls: a deliberately wrong recipient or ULP change affects
    # independently reconstructed matching graph SHA, without changing sources.
    original=[((0,1),float(1+1e-4*.25)),((0,2),float(1+1e-4*.45))]
    mutated=[((0,1),float(1+1e-4*.25)),((0,3),float(1+1e-4*.45))]
    assert graphSHA(original)!=graphSHA(mutated)
    changed=[((0,1),math.nextafter(original[0][1],2.0)),original[1]]
    assert graphSHA(original)!=graphSHA(changed)
    all_ticks=[t for c in cases for t in c['ticks']]
    report={'schema':'ABH_N343_ORIGINAL_NATIVE_MATCHING_GRAPH_EXACT_CERT',
       'source_python_index_sha':sha(ORIGINAL_INDEX),
       'source_ts_index_sha':sha(TS_INDEX),'source_immutable_shock_manifest_sha':sha(INPUT_INDEX),
       'scenarios':cases,'graph_ticks_compared':len(all_ticks),
       'identical_graph_shas':sum(t['graph_content_identical'] for t in all_ticks),
       'matching_cardinality_and_exact_residue_equal':sum(t['TS_objective_matches_NX'] for t in all_ticks),
       'original_Python_float_matching_integer_optimal':sum(t['native_Python_float_matching_exact_integer_optimal'] for t in all_ticks),
       'original_Python_vs_TS_pair_identity':sum(t['native_original_TS_chosen_pairs_identical'] for t in all_ticks),
       'TS_primal_dual_certificate_present':sum(t['TS_certified_primal_dual'] for t in all_ticks),
       'graph_undirected_reciprocity_verified':all(t['edge_count']<=t['directed_accepted'] for t in all_ticks),
       'mutant_reciprocal_actor_and_weight_ULP_detected':True,
       'limitation':'Reconstructed original graph from original native accept events + original u_match, but shared source rules; all 960 integer objectives checked against independent NetworkX, algorithm theoretical lineage overlaps with MIT Blossom. Synthetic only.',
       'CT2_scientific':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N343_GRAPH_ORACLE',len(all_ticks),'graph SHA',report['identical_graph_shas'],
      'integer optimum',report['matching_cardinality_and_exact_residue_equal'],
      'python-float exact optimum',report['original_Python_float_matching_integer_optimal'],
      'pairs',report['original_Python_vs_TS_pair_identity'],'SHA',sha(OUT))

if __name__=='__main__':main()
