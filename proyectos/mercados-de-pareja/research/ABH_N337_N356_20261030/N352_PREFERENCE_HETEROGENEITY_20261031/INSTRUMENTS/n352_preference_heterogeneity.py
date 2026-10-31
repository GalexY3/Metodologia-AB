"""N352 preregistered DA proposer-side sensitivity to exogenous actor-specific
preference heterogeneity on the SAME 96 fixed native ESBM opportunity graphs.

The preferences are assumptions, NOT recorded by human or simulated actors.
No source matching graph, shock or observed acceptance is altered.
"""
import hashlib
import json
from pathlib import Path
from n351_da_central import da,blocking,canonical

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'N351_BIPARTITE_INPUTS.json'
RESULT=ROOT/'outcomes'/'N351_DA_CENTRAL.json'
OUT=ROOT/'outcomes'/'N352_PREFERENCE_HETEROGENEITY.json'
LAMBDAS=[0.0,0.1,0.5,1.0,2.0]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def actor_noise(seed,t,i,j):
    payload=f"N352|{seed}|{t}|{i}|{j}|RECEIVER".encode()
    val=int.from_bytes(hashlib.sha256(payload).digest()[:8],byteorder='big')
    return val/(2**64)-0.5
def make_prefs(m,lam,people):
    accepted={i:[] for e in m['edges'] for i in e}
    for a,b in m['edges']:accepted[a].append(b);accepted[b].append(a)
    prefs={}
    for i,partners in accepted.items():
        def score(j):
            common=(people['q'][j]-0.02*abs(people['age'][i]-people['age'][j])
                +0.03*(people['norm'][i]==people['norm'][j])-1e-7*j)
            # At lambda 0 exactly mirror N351 fixed ranks.
            return round(common+lam*actor_noise(m['seed'],m['t'],i,j),12)
        prefs[str(i)]=sorted(partners,key=lambda j:(-score(j),j))
    return prefs
def main():
    if OUT.exists():raise SystemExit('OUTPUT_PREEXISTS')
    assert sha(SOURCE)=='42c24b43bde724d0609d816a57f6287c17c0f201705382031d8f00cecfe28d35'
    assert sha(RESULT)=='5bc1d9e7557e6e090002a1b705fbf1f08691bd736de50ea418c52ba800a72eac'
    src=json.loads(SOURCE.read_text());old=json.loads(RESULT.read_text())
    assert len(src['markets'])==len(old['results'])==96
    out=[]
    for seed in [101,211,307,401,503,601]:
        manifest=json.loads((ROOT/'N341_INPUT_MANIFEST.json').read_text())
        p=next(x for x in manifest['rows'] if x['seed']==seed)['people']
        filepath=ROOT/'official_inputs_60'/p['path']
        assert sha(filepath)==p['sha256']
        people=json.loads(filepath.read_text())
        for m,oldrow in zip(src['markets'],old['results']):
            if m['seed']!=seed:continue
            assert (m['seed'],m['t'])==(oldrow['seed'],oldrow['t'])
            for lam in LAMBDAS:
                prefs=make_prefs(m,lam,people)
                if lam==0.0:assert prefs==m['preferences']
                F=da(m['women'],m['men'],prefs)
                M=da(m['men'],m['women'],prefs)
                assert len(F)==len(M)
                assert len(blocking(F,m['edges'],prefs))==len(blocking(M,m['edges'],prefs))==0
                central=canonical(m['central_pairs'])
                x={'seed':seed,'t':m['t'],'lambda':lam,
                   'edge_count':len(m['edges']),
                   'DA_F_pairs':F,'DA_M_pairs':M,
                   'same_da_pairs':F==M,
                   'DA_count':len(F),
                   'central_count':len(central),
                   'central_blocking':len(blocking(central,m['edges'],prefs)),
                   'DA_F_central_overlap':len(set(map(tuple,F))&set(map(tuple,central)))}
                if lam==0.0:
                    assert F==oldrow['protocols']['DA_F']['pairs']
                    assert M==oldrow['protocols']['DA_M']['pairs']
                out.append(x)
    assert len(out)==480
    report={'schema':'N352_DA_PREFERENCE_HETEROGENEITY_SENSITIVITY',
      'original_96_market_sha':sha(SOURCE),
      'original_DA_baseline_sha':sha(RESULT),
      'lambdas':LAMBDAS,'cases':out,'summary':{
         str(lam):{
           'markets':sum(x['lambda']==lam for x in out),
           'DA_F_vs_M_different_markets':sum(x['lambda']==lam and not x['same_da_pairs'] for x in out),
           'DA_pairs':sum(x['DA_count'] for x in out if x['lambda']==lam),
           'central_blocking_pairs':sum(x['central_blocking'] for x in out if x['lambda']==lam),
           'mean_DA_F_overlap_central':sum(x['DA_F_central_overlap'] for x in out if x['lambda']==lam)/96
         } for lam in LAMBDAS},
      'no_human_preferences_observed':True,'CT2':7,'STOP_R5_human':True}
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('N352_HETEROGENEITY',report['summary'],'SHA',sha(OUT))
if __name__=='__main__':main()
