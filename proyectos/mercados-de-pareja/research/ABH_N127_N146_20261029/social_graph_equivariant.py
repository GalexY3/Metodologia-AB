"""Degree-preserving synthetic graph null built on invariant q-rank coordinates.
q is an artificial latent index; exact ties are excluded by contract.
Unlike the previous baseline, rewiring PRNG sees canonical rank IDs, not actor labels.
"""
import networkx as nx
import numpy as np
from social_graph import edge_mask,scheduler,stats
def build(p,seed,kind):
 q=np.asarray(p['q']);n=len(q)
 assert n>=8 and n%2==0 and len(set(q.tolist()))==n,'Unique latent rank required'
 order=list(map(int,np.argsort(q,kind='stable')))
 canonical=nx.Graph();canonical.add_nodes_from(range(n))
 for i in range(n):
  for delta in (1,2):canonical.add_edge(i,(i+delta)%n)
 assert all(deg==4 for _,deg in canonical.degree())
 if kind=='rewired':
  nx.connected_double_edge_swap(canonical,nswap=min(32,2*n),_window_threshold=3,seed=int(seed)+837)
 elif kind!='ring':raise ValueError('Network kind must ring/rewired')
 g=nx.relabel_nodes(canonical,{i:order[i] for i in range(n)},copy=True)
 assert nx.is_connected(g) and len(g.edges())==2*n and all(deg==4 for _,deg in g.degree())
 return g
