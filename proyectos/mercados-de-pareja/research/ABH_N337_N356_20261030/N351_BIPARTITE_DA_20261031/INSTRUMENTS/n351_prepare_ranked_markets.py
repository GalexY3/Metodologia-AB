"""Inputs ONLY: derive ex ante ordinal preference lists from synthetic actor traits
and actual original ESBM mutual-YES opportunities for 96 bipartite markets.
Not a claim that real subjects revealed rankings; no DA/matching computed here.
"""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parent.parent
IDX=ROOT/'outcomes'/'N342_NATIVE_INDEX.json'
MAN=ROOT/'N341_INPUT_MANIFEST.json'
OUT=ROOT/'N351_BIPARTITE_INPUTS.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def score(people,i,j):
    # Observer-independent directional rank: attractive receiver q, age distance,
    # shared norm; last term only stable deterministic ID tie-break.
    return round(people['q'][j]-0.02*abs(people['age'][i]-people['age'][j])
         +0.03*(people['norm'][i]==people['norm'][j])-1e-7*j,12)
def main():
    if OUT.exists():raise SystemExit('INPUT_ALREADY_EXISTS')
    idx=json.loads(IDX.read_text())['rows'];manifest=json.loads(MAN.read_text())
    markets=[]
    for seed in [101,211,307,401,503,601]:
      p=next(x for x in manifest['rows'] if x['seed']==seed)['people']
      filepath=ROOT/'official_inputs_60'/p['path']
      assert sha(filepath)==p['sha256']
      people=json.loads(filepath.read_text())
      women=[i for i,g in enumerate(people['genders']) if g=='F']
      men=[i for i,g in enumerate(people['genders']) if g=='M']
      row=next(x for x in idx if x['seed']==seed and x['scenario']=='heterosexual_restricted')
      fp=ROOT/'outcomes'/row['trace_path'];rf=ROOT/'outcomes'/row['run_path']
      assert sha(fp)==row['trace_sha256'] and sha(rf)==row['run_sha256']
      central=json.loads(rf.read_text())['formation_pairs_by_tick']
      accepted=[[] for _ in range(16)]
      with fp.open(encoding='utf8') as fh:
        for line in fh:
          e=json.loads(line)
          if e['stage']=='response' and e['decision']:
            a,b=sorted((e['i'],e['j']))
            assert {people['genders'][a],people['genders'][b]}=={'F','M'}
            accepted[e['t']].append([a,b])
      for t in range(16):
        # One undirected eligibility edge per dyad even if the original trace
        # reports directed reciprocation twice in the same period.
        edges=[list(z) for z in sorted(set(tuple(z) for z in accepted[t]))]
        elig=sorted(set(i for e in edges for i in e))
        # every candidate is mutually acceptable by constructed definition
        prefs={}
        for i in elig:
          partners=sorted([b if a==i else a for a,b in edges if a==i or b==i],
                          key=lambda j:(-score(people,i,j),j))
          prefs[str(i)]=partners
        markets.append({'seed':seed,'t':t,'scenario':'heterosexual_restricted',
          'women':women,'men':men,'edges':edges,'central_pairs':central[t],
          'positive_directional_response_events':len(accepted[t]),
          'preferences':prefs,'definition':'ASSUMED q(receiver)-0.02 age gap +0.03 same_norm -1e-7 id rank',
          'original_native_trace_sha':row['trace_sha256'],'original_native_result_sha':row['run_sha256']})
    assert len(markets)==96
    payload={'schema':'N351_BIPARTITE_CONDITIONAL_ORDINAL_MARKETS_V1',
     'original_native_index_sha':sha(IDX),'original_seed_input_manifest_sha':sha(MAN),
     'market_count':96,'unit':'seed by ESBM tick, heterogeneous exposure and first-date mutual YES observed ONLY within synthetic ESBM',
     'ordinal_assumption':'Synthetic independent actor ordinal ranks, never inferred from yes or transformed into observed preference',
     'markets':markets}
    OUT.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N351_INPUTS_FROZEN',len(markets),sha(OUT))
if __name__=='__main__':main()
