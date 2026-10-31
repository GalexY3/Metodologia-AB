"""N351 prospective: DA proposer side x2 vs exact central and greedy on same
native artificial opportunity graph, under separately assumed actor rankings.
"""
from pathlib import Path
import hashlib,json,math
import networkx as nx

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'N351_BIPARTITE_INPUTS.json'
OUT=ROOT/'outcomes'/'N351_DA_CENTRAL.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return sorted([sorted((a,b)) for a,b in x])
def da(prop,recv,prefs):
  # Independent from central blossom; each proposer continues through
  # their explicit strict incomplete acceptable ranking.
  pos={u:{v:i for i,v in enumerate(prefs.get(str(u),[]))} for u in recv}
  nextidx={u:0 for u in prop}
  free=list(prop);holding={}
  while free:
    u=free.pop(0)
    p=prefs.get(str(u),[])
    if nextidx[u]>=len(p):continue
    v=p[nextidx[u]];nextidx[u]+=1
    if u not in pos.get(v,{}):raise RuntimeError('NOT_MUTUALLY_ACCEPTABLE')
    if v not in holding:holding[v]=u
    else:
      incumbent=holding[v]
      if pos[v][u]<pos[v][incumbent]:
        holding[v]=u;free.append(incumbent)
      else:free.append(u)
  return canonical([[u,v] for v,u in holding.items()])
def blocking(pairs,edges,prefs):
  partners={a:b for a,b in pairs}|{b:a for a,b in pairs}
  rankings={int(a):{v:i for i,v in enumerate(lst)} for a,lst in prefs.items()}
  def better(a,b):
    current=partners.get(a,None)
    return current is None or rankings[a][b]<rankings[a][current]
  return sorted([e for e in edges if tuple(e) not in {tuple(z) for z in pairs} and
                  better(e[0],e[1]) and better(e[1],e[0])])
def greedy(edges,reverse=False):
  used=set();pairs=[]
  for a,b in reversed(edges) if reverse else edges:
    if a not in used and b not in used:
      used|={a,b};pairs.append([a,b])
  return canonical(pairs)
def main():
  if OUT.exists():raise SystemExit('NO_OVERWRITE')
  data=json.loads(SOURCE.read_text());assert len(data['markets'])==96
  rows=[]
  for m in data['markets']:
    w,men=m['women'],m['men'];prefs=m['preferences'];edges=m['edges']
    central=canonical(m['central_pairs'])
    fem=da(w,men,prefs);male=da(men,w,prefs)
    # independent cardinality baseline exact blossom and known original pairs
    graph=nx.Graph();graph.add_nodes_from(w+men);graph.add_edges_from(edges)
    maxcard=len(nx.max_weight_matching(graph,maxcardinality=True,weight=None))
    assert len(central)==maxcard
    candidates={'central':central,'DA_F':fem,'DA_M':male,
                'greedy_forward':greedy(edges),'greedy_reverse':greedy(edges,True)}
    row={'seed':m['seed'],'t':m['t'],'edges':len(edges),'maximum_cardinality':maxcard,
         'protocols':{name:{'pairs':pairs,'count':len(pairs),
          'blocking_pairs':len(blocking(pairs,edges,prefs)),
          'blocking_witnesses':blocking(pairs,edges,prefs)[:8]} for name,pairs in candidates.items()}}
    assert row['protocols']['DA_F']['blocking_pairs']==0 and row['protocols']['DA_M']['blocking_pairs']==0
    assert len(fem)==len(male)
    rows.append(row)
  result={'schema':'N351_SYNTHETIC_RANKED_DA_VS_CENTRAL', 'input_sha256':sha(SOURCE),
      'runs':96,'results':rows,'summary':{name:{
       'pairs':sum(x['protocols'][name]['count'] for x in rows),
       'markets_with_blocking_pair':sum(x['protocols'][name]['blocking_pairs']>0 for x in rows),
       'total_blocking_pairs':sum(x['protocols'][name]['blocking_pairs'] for x in rows)} for name in
       ['central','DA_F','DA_M','greedy_forward','greedy_reverse']},
      'DA_F_vs_DA_M_different_pairsets':sum(x['protocols']['DA_F']['pairs']!=x['protocols']['DA_M']['pairs'] for x in rows),
      'DA_vs_central_pairsets_different':sum(x['protocols']['DA_F']['pairs']!=x['protocols']['central']['pairs'] for x in rows),
      'synthetic_ordinal_preferences_assumed_not_observed':True,'human_rows':0,'CT2':7,'STOP_R5_human':True}
  OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
  print('N351_DA',result['summary'], 'DA_F_M_DIFFERENT',result['DA_F_vs_DA_M_different_pairsets'],sha(OUT))
if __name__=='__main__':main()
