"""Synthetic degree-preserving opportunity graphs (not human social networks)."""
import networkx as nx
import numpy as np
import esbm_event_engine as engine
import mini_world as mini
def build(p,seed,kind):
 n=len(p['q'])
 assert n>=8 and n%2==0
 rank=list(np.argsort(p['q'],kind='stable'))
 g=nx.Graph();g.add_nodes_from(range(n))
 for pos,i in enumerate(rank):
  for offset in (1,2):
   j=rank[(pos+offset)%n]
   g.add_edge(int(i),int(j))
 assert len(g.edges())==n*2 and all(d==4 for _,d in g.degree())
 if kind=='rewired':
  nx.connected_double_edge_swap(g,nswap=min(32,n*2),_window_threshold=3,seed=int(seed)+837)
 elif kind!='ring':
  raise ValueError('Unknown network '+str(kind))
 assert nx.is_connected(g) and all(d==4 for _,d in g.degree())
 return g
def edge_mask(g,n):
 arr=np.zeros((n,n),bool)
 for i,j in g.edges():arr[i,j]=arr[j,i]=True
 assert not np.diag(arr).any()
 return arr
def scheduler(graph,base_mode='pair_max'):
 mask=edge_mask(graph,len(graph.nodes))
 def exposed(p,eligible,available,config,seen,t,mode,slots):
  allowed=eligible&mask
  return engine.opportunities(p,allowed,available,config,seen,t,base_mode,slots)
 return exposed
def stats(g,p,eligible):
 edges=list(g.edges())
 return dict(edges=len(edges),degree_sequence=sorted(dict(g.degree()).values()),connected=nx.is_connected(g),
             eligible_edges=sum(bool(eligible[i,j]) for i,j in edges),
             cross_norm_edges=sum(int(p['norm'][i]!=p['norm'][j]) for i,j in edges),
             mean_quality_difference=float(np.mean([abs(p['q'][i]-p['q'][j]) for i,j in edges])))
