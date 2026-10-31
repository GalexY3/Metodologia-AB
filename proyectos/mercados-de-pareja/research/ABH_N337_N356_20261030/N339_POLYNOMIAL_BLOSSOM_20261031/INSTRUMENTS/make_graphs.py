"""Prospectively construct GRAPH INPUTS only (never compute matching outcomes)."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
SCALE=2**52

def weight(u):
    return float(1.0+1e-4*float(u))

def add(name,n,raw,graphs):
    used=set();edges=[]
    for a,b,w in raw:
        a=int(a);b=int(b)
        if a>b:a,b=b,a
        assert 0<=a<b<n and (a,b) not in used and 1<=w<1.000101
        assert ((w-1.0)*SCALE).is_integer()
        used.add((a,b));edges.append([a,b,float(w)])
    edges.sort(key=lambda e:(e[0],e[1]))
    graphs.append({'name':name,'n':n,'edges':edges})

def main():
    dest=ROOT/'GRAPH_INPUTS_N339.json'
    if dest.exists():raise SystemExit('INPUTS_PREEXIST')
    rng=np.random.default_rng(332023)
    graphs=[]
    add('C4_EXACT_TIE',4,[(0,1,1.0),(1,2,1.0),(2,3,1.0),(3,0,1.0)],graphs)
    add('K6_ALL_TIED',6,[(i,j,1.0) for i in range(6) for j in range(i+1,6)],graphs)
    add('ODD_TRIANGLE_PENDANT',8,[(0,1,weight(.71)),(1,2,weight(.69)),(0,2,weight(.11)),
        (0,3,weight(.95)),(2,4,weight(.31)),(4,5,weight(.92)),(5,6,weight(.1)),
        (6,7,weight(.84)),(3,7,weight(.12))],graphs)
    for n,d in [(12,.65),(14,.80),(24,.32),(64,.12),(144,.08),(144,.31)]:
        edges=[]
        for i in range(n):
            for j in range(i+1,n):
                if rng.random()<d:
                    edges.append((i,j,weight(rng.random())))
        add('RANDOM_N'+str(n)+'_D'+str(int(d*100)),n,edges,graphs)
    for n,d in [(144,.13),(144,.27)]:
        edges=[]
        for i in range(n):
            for j in range(i+1,n):
                if rng.random()<d:
                    # Exponent 0 binary64 ULPs: intentionally many ties/near-ties.
                    edges.append((i,j,1.0+int(rng.integers(0,12))*2**-52))
        add('ULP_N'+str(n)+'_D'+str(int(d*100)),n,edges,graphs)
    # Multiple disconnected large components, degree-zero vertices, strongly non-bipartite.
    edges=[]
    for lo,hi in [(0,33),(34,72),(73,109)]:
        for i in range(lo,hi):
            for j in range(i+1,hi):
                if rng.random()<.23:edges.append((i,j,weight(rng.random())))
    add('DISCONNECTED_N144_WITH_ISOLATES',144,edges,graphs)
    payload={'schema':'ABH_N339_GRAPH_INPUTS_NO_OUTCOMES','rng_seed':332023,
             'weights':'binary64 1 + 1e-4*u or 1 + k*ULP',
             'n_cases':len(graphs),'cases':graphs}
    dest.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n',encoding='utf8')
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    print('INPUTS_ONLY',len(graphs),dest.stat().st_size,digest)

if __name__=='__main__':main()
