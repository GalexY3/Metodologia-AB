"""V13 graph interventions on unchanged V12 reward, actor and optimizer.

Graph variants: original ring, 2-D torus, small-world torus, random regular,
four communities, preferential attachment hubs, geometric graphs on a
jittered lattice or on a binomial point process. All share N and the same
actor's per-color features; per-agent weights remain independent.

Crucial: Jittered lattice (hyperuniform support) is NOT automatically
multihyperuniform profession marks. The latter are evaluated separately.
"""
from __future__ import annotations
from functools import lru_cache
import importlib,sys,math
from pathlib import Path
import numpy as np
import networkx as nx
import torch
from torch.nn import functional as F
HERE=Path(__file__).resolve().parent
V12_DIR=HERE.parent/'v12_variable_mk'
sys.path.insert(0,str(V12_DIR))
import v12 as base
BASE_WORLD=base.World
ORIGINAL_GRAPH=base.graph
base.ROOT=HERE
TOPO_SEED=None
TOPO_CHOICES=('ring','torus','smallworld','random_regular','modular','hubs','jitter_geo','poisson_geo')

def grid_shape(n):
    pairs=[(a,n//a) for a in range(2,math.isqrt(n)+1) if n%a==0]
    if not pairs:raise ValueError('Spatial MHU needs composite N')
    return min(pairs,key=lambda p:abs(p[0]-p[1]))

def coordinates(n,topology='torus',seed=0):
    h,w=grid_shape(n)
    xy=np.array([((i%w+.5)/w,(i//w+.5)/h) for i in range(n)],dtype=float)
    rng=np.random.default_rng(seed)
    if topology=='jitter_geo':
        xy=(xy+rng.uniform(-.23,.23,size=xy.shape)/np.array([w,h]))%1
    elif topology=='poisson_geo':
        xy=rng.random((n,2))
    return xy

def torus_graph(n,degree):
    h,w=grid_shape(n)
    offsets=[(1,0),(-1,0),(0,1),(0,-1),
             (1,1),(-1,-1),(1,-1),(-1,1),
             (2,0),(-2,0),(0,2),(0,-2)]
    if degree not in (4,6,8,10,12):
        raise ValueError('Torus supports degree 4, 6, 8, 10, 12')
    if degree==6:
        selected=offsets[:4]+offsets[8:10]
    else:
        selected=offsets[:degree]
    g=nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        x=i%w;y=i//w
        for dx,dy in selected:
            j=((y+dy)%h)*w+(x+dx)%w
            if j!=i:g.add_edge(i,j)
    if any(deg!=degree for _,deg in g.degree()):
        raise AssertionError(('torus_degree',n,degree,sorted(set(dict(g.degree()).values()))))
    return g

def modular_graph(n,degree,seed):
    rng=np.random.default_rng(seed)
    if n%4:raise ValueError('Modular topology requires N divisible by 4')
    block=n//4
    if degree>=block or (degree*block)%2:raise ValueError('modular degree invalid')
    g=nx.Graph()
    g.add_nodes_from(range(n))
    for c in range(4):
        sub=nx.random_regular_graph(degree,block,seed=seed+13*c)
        g.add_edges_from((a+c*block,b+c*block) for a,b in sub.edges)
    # Swap intra-community links across adjacent communities to create sparse
    # bridges while retaining EVERY degree and the same number of edges.
    for c in range(3):
        left=[(a,b) for a,b in g.edges if a//block==c and b//block==c]
        right=[(a,b) for a,b in g.edges if a//block==c+1 and b//block==c+1]
        rng.shuffle(left);rng.shuffle(right)
        for (a,b) in left:
            found=False
            for (u,v) in right:
                if not g.has_edge(a,u) and not g.has_edge(b,v):
                    g.remove_edge(a,b);g.remove_edge(u,v)
                    g.add_edge(a,u);g.add_edge(b,v);found=True;break
            if found:break
        if not found:raise RuntimeError('Cannot create intercommunity bridge')
    if not nx.is_connected(g):
        # It is possible for a degree-regular subgraph to disconnect after
        # swapping. Reject, never silently claim connected modular graph.
        raise RuntimeError('modular graph disconnected')
    return g

def spatial_graph(n,degree,topology,seed):
    points=coordinates(n,topology,seed)
    delta=points[:,None,:]-points[None,:,:]
    delta-=np.round(delta)
    dist=np.linalg.norm(delta,axis=-1)
    whole=nx.Graph()
    whole.add_nodes_from(range(n))
    edges=sorted([(float(dist[i,j]),i,j) for i in range(n) for j in range(i+1,n)])
    # Torus-Euclidean MST first: no isolated individuals; then shortest pairs.
    ordered=nx.Graph()
    ordered.add_nodes_from(range(n))
    ordered.add_weighted_edges_from((a,b,l) for l,a,b in edges)
    tree=nx.minimum_spanning_tree(ordered)
    g=nx.Graph(tree)
    target=max(n-1,round(n*degree/2))
    for length,a,b in edges:
        if g.number_of_edges()>=target:break
        if not g.has_edge(a,b):g.add_edge(a,b)
    assert g.number_of_edges()==target and nx.is_connected(g)
    return g

@lru_cache(maxsize=128)
def build_graph(n,degree,topology,seed):
    if topology not in TOPO_CHOICES:raise ValueError(topology)
    if topology=='ring':
        a=ORIGINAL_GRAPH(n,degree,'ring',seed)
        g=nx.Graph();g.add_nodes_from(range(n))
        for i,row in enumerate(a):
            g.add_edges_from((i,int(v)) for v in row)
    elif topology=='torus':
        g=torus_graph(n,degree)
    elif topology=='smallworld':
        g=torus_graph(n,degree)
        swaps=round(.15*g.number_of_edges())
        nx.double_edge_swap(g,nswap=swaps,max_tries=swaps*30,seed=seed)
    elif topology=='random_regular':
        g=nx.random_regular_graph(degree,n,seed=seed)
    elif topology=='modular':
        g=modular_graph(n,degree,seed)
    elif topology=='hubs':
        g=nx.barabasi_albert_graph(n,max(1,degree//2),seed=seed)
    else:
        g=spatial_graph(n,degree,topology,seed)
    assert set(g.nodes)==set(range(n))
    assert nx.is_connected(g),(topology,n,degree,seed)
    sizes=np.array([g.degree(i) for i in range(n)])
    pad=np.full((n,max(sizes)), -1,dtype=np.int64)
    for i in range(n):
        neigh=sorted(g.neighbors(i))
        pad[i,:len(neigh)]=neigh
    return pad

def graph_v13(n,degree,topology,seed):
    return build_graph(n,degree,topology,TOPO_SEED if TOPO_SEED is not None else seed)

class WorldV13(BASE_WORLD):
    def local(self):
        if self.c.blind:
            return torch.zeros(self.c.batch,self.c.n,self.c.m,device=self.c.device)
        valid=self.adj>=0
        ids=self.adj.clamp_min(0)
        encoded=F.one_hot(self.jobs[:,ids],num_classes=self.c.m).float()
        return (encoded*valid[None,:,:,None]).sum(2)/valid.sum(1)[None,:,None]
    def reception(self,intentions):
        if self.c.blind:
            return torch.zeros(self.c.batch,self.c.n,self.c.m,device=self.c.device)
        valid=self.adj>=0
        ids=self.adj.clamp_min(0)
        encoded=F.one_hot(intentions[:,ids],num_classes=self.c.m).float()
        return (encoded*valid[None,:,:,None]).sum(2)/valid.sum(1)[None,:,None]

base.graph=graph_v13
base.World=WorldV13

def network_stats(n,degree,topology,seed):
    pad=build_graph(n,degree,topology,seed)
    g=nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i,int(j)) for i,row in enumerate(pad) for j in row if j>=0)
    deg=np.array([g.degree(i) for i in range(n)])
    xy=coordinates(n,topology,seed)
    edgelength=[]
    for a,b in g.edges:
        dist=xy[a]-xy[b];dist-=np.round(dist)
        edgelength.append(float(np.linalg.norm(dist)))
    h,w=grid_shape(n)
    districts={i:(i//w>=h//2)*2+(i%w>=w//2) for i in range(n)}
    groups=[set(i for i,d in districts.items() if d==k) for k in range(4)]
    return dict(n=n,network=topology,requested_mean_degree=degree,
      mean_degree=float(deg.mean()),min_degree=int(deg.min()),max_degree=int(deg.max()),
      degree_std=float(deg.std()),links=int(g.number_of_edges()),
      clustering=float(nx.average_clustering(g)),path_length=float(nx.average_shortest_path_length(g)),
      spatial_edge_length=float(np.mean(edgelength)),modularity=float(nx.community.modularity(g,groups)),
      coordinate_layout=('perturbed-lattice' if topology=='jitter_geo' else 'binomial-uniform' if topology=='poisson_geo' else 'fixed-grid'),
      graph_seed=seed)

def run_cli():
    import argparse
    pre=argparse.ArgumentParser(add_help=False)
    pre.add_argument('--network',choices=TOPO_CHOICES,required=True)
    pre.add_argument('--graph-seed',type=int,default=None)
    selected,rest=pre.parse_known_args()
    sys.argv=[sys.argv[0]]+rest
    args=base.parse()
    args.topology=selected.network
    global TOPO_SEED
    TOPO_SEED=selected.graph_seed if selected.graph_seed is not None else args.seed+889
    out=HERE/'runs'/args.name
    out.mkdir(parents=True,exist_ok=True)
    info=network_stats(args.n,args.degree,selected.network,TOPO_SEED)
    path=out/'NETWORK.json'
    if path.exists():
        import json
        if json.loads(path.read_text('utf8'))!=info:raise RuntimeError('Network differs from existing run')
    base.write_json(path,info)
    print('NETWORK',info,flush=True)
    base.run(args)

if __name__=='__main__':run_cli()
