"""Independent NetworkX check of N344 uniqueness for all 120 boundary ticks.

Also validates all reported nonunique witnesses if fewer than 200.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import networkx as nx

ROOT=Path(__file__).resolve().parent.parent
SCALE=2**52

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    out=ROOT/'outcomes'/'N344_INDEPENDENT_SAMPLE.json'
    if out.exists():raise SystemExit('NO_OVERWRITE')
    idx=json.loads((ROOT/'N341_INPUT_MANIFEST.json').read_text())
    nidx=json.loads((ROOT/'outcomes'/'N342_NATIVE_INDEX.json').read_text())
    tsidx=json.loads((ROOT/'outcomes'/'N341_TS60_INDEX.json').read_text())
    data=json.loads((ROOT/'outcomes'/'N344_UNIQUENESS.json').read_text())
    assert len(data['cases'])==960
    selected={(z['seed'],z['scenario'],z['t']) for z in data['cases'] if z['t'] in (0,15)}
    other=[z for z in data['cases'] if z['proven_nonunique'] and (z['seed'],z['scenario'],z['t']) not in selected]
    if len(other)>200:other=other[:200]
    selected.update((z['seed'],z['scenario'],z['t']) for z in other)
    assert len(selected)>=120
    rows=[]
    for seed_info in idx['rows']:
        seed=seed_info['seed'];meta=seed_info['tensors']['u_match']
        tensorpath=ROOT/'official_inputs_60'/meta['path']
        assert sha(tensorpath)==meta['sha256']
        tensor=np.memmap(tensorpath,dtype='<f8',mode='r',shape=(16,144,144))
        for name in idx['scenario_order']:
            trials=[z for z in data['cases'] if z['seed']==seed and z['scenario']==name and (seed,name,z['t']) in selected]
            if not trials:continue
            p=next(z for z in nidx['rows'] if z['seed']==seed and z['scenario']==name)
            j=next(z for z in tsidx['rows'] if z['seed']==seed and z['scenario']==name)
            assert sha(ROOT/'outcomes'/p['trace_path'])==p['trace_sha256']
            accepted=[[] for _ in range(16)]
            with (ROOT/'outcomes'/p['trace_path']).open(encoding='utf8') as f:
                for line in f:
                    e=json.loads(line)
                    if e['stage']=='response' and e['decision']:
                        a,b=sorted((e['i'],e['j']))
                        accepted[e['t']].append((a,b))
            ts=json.loads((ROOT/'outcomes'/j['run_file']).read_text())
            for row in trials:
                t=row['t'];edges={k:int((float(1+1e-4*tensor[t,k[0],k[1]])-1)*SCALE) for k in accepted[t]}
                G=nx.Graph();G.add_nodes_from(range(144))
                G.add_weighted_edges_from((a,b,w) for (a,b),w in edges.items())
                pairset=ts['formation_pairs_by_tick'][t]
                reference=(len(pairset),sum(edges[tuple(x)] for x in pairset))
                alt_found=False
                for e in pairset:
                    H=G.copy();H.remove_edge(*e)
                    match=nx.max_weight_matching(H,maxcardinality=True,weight='weight')
                    alternative=(len(match),sum(edges[tuple(sorted(x))] for x in match))
                    assert alternative<=reference,('FROZEN_MATCH_BELOW_ALTERNATIVE',seed,name,t)
                    if alternative==reference:
                        alt_found=True;break
                assert alt_found==row['proven_nonunique'],('UNIQUENESS_DISAGREEMENT',seed,name,t)
                assert (not alt_found)==row['proven_unique'] if not row['unresolved'] else True
                rows.append({'seed':seed,'scenario':name,'t':t,'independent_NX_confirmed':True,
                  'nonunique':alt_found,'selected_pairs':len(pairset),'optimal_residue':reference[1]})
    report={'schema':'N344_INDEPENDENT_NETWORKX_EXCLUSION_AUDIT',
      'N344_JS_source_sha':sha(ROOT/'outcomes'/'N344_UNIQUENESS.json'),
      'sample_rule':'t=0 and t=15 each of 60 runs (120) plus up to first 200 other nonunique tick witnesses',
      'cases_checked':len(rows),'all_confirmed':len(rows),
      'cases':rows,'CT2':7,'STOP_R5_human':True}
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('N344_PY_INDEPENDENT_AUDIT',len(rows),'of',len(selected),'SHA',sha(out))

if __name__=='__main__':main()
