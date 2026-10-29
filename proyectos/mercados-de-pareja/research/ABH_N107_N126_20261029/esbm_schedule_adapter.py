"""Non-destructive ESBM 2.x encounter-scheduling adapter.
Loads and checks original esbm_dynamic.py SHA256 before in-memory source transform;
'legacy' is required to agree exactly. NOT human-population calibration.
This transformation is intentionally strict: upstream changes fail closed.
"""
from __future__ import annotations
import hashlib
import inspect
import itertools
from pathlib import Path
import numpy as np
import networkx as nx
import esbm_dynamic as original

SOURCE_SHA256 = 'f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
ORIGINAL_FILE = Path(original.__file__)
assert hashlib.sha256(ORIGINAL_FILE.read_bytes()).hexdigest() == SOURCE_SHA256, 'Origin changed: stop, audit source first'

# The two functions below replicate the original Gumbel selection for legacy mode.
# Institution modes schedule disjoint *unordered* meetings; one actor sends a proposal,
# the other replies conditionally. Thus the proposals/replies are NOT two independent
# observed native yes/no decisions of humans.
def opportunities(p, eligible, available, config, seen, tick, mode='legacy', slots=1):
    available = tuple(map(int, available))
    if mode == 'legacy':
        for i in available:
            candidates = np.array([j for j in available if j != i and eligible[i, j]], dtype=int)
            if not len(candidates):
                continue
            kk = min(original.K, len(candidates))
            scores = -np.log(-np.log(np.clip(p['u_expose'][tick, i, candidates], 1e-12, 1-1e-12)))
            if config['policy'] == 'same_norm':
                scores += 1.7 * (p['norm'][candidates] == p['norm'][i])
            elif config['policy'] == 'popular':
                scores += 3.5 * (p['q'][candidates] - .5)
            elif config['policy'] == 'balance':
                scores += -1.4 * np.log1p(seen[candidates])
            for j in candidates[np.argsort(scores)[-kk:]]:
                yield int(i), int(j)
        return
    if mode not in ('pair_max', 'pair_greedy', 'pair_budgeted_max'):
        raise ValueError('Unknown institution: '+str(mode))
    if slots != 1:
        raise ValueError('Initial institution contract: exactly one encounter per actor per tick')
    # Same available population and eligible undirected edges for strong comparisons.
    # Weight = symmetric deterministic Gumbel shock, independent of actor ID ordering.
    # Actual fitted propensity/model of venue assignment is NOT claimed.
    edges = []
    for x, i in enumerate(available):
        for j in available[x+1:]:
            if not eligible[i, j]:
                continue
            a = float(p['u_expose'][tick, i, j]); b = float(p['u_expose'][tick, j, i])
            weight = -np.log(-np.log(np.clip(a, 1e-12, 1-1e-12))) + -np.log(-np.log(np.clip(b, 1e-12, 1-1e-12)))
            edges.append((i, j, weight))
    # Prospectively repaired N108: cap feasible candidate shortlists to top four
    # directed opportunity shocks per actor, then take the undirected union.
    # This restricts the graph; max matching is exact only within this shortlist.
    shortlist=set()
    for i in available:
        candidates=np.array([j for j in available if j!=i and eligible[i,j]],dtype=int)
        if not len(candidates):continue
        chosen=candidates[np.argsort(p['u_expose'][tick,i,candidates])[-min(4,len(candidates)):]]
        for j in chosen: shortlist.add((min(i,int(j)),max(i,int(j))))
    edges=[(i,j,w) for i,j,w in edges if (i,j) in shortlist]
    edges.sort(key=lambda x:-x[2])
    used = set(); greedy = []
    for i, j, w in edges:
        if i not in used and j not in used:
            used.add(i); used.add(j); greedy.append((i,j,w))
    if mode == 'pair_greedy':
        selected = greedy
    else:
        G = nx.Graph(); G.add_nodes_from(available)
        G.add_weighted_edges_from(edges)
        matches = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True, weight='weight')
        selected = [(min(i,j), max(i,j), G[i][j]['weight']) for i,j in matches]
        selected.sort(key=lambda x:-x[2])
        if mode == 'pair_budgeted_max':
            selected = selected[:len(greedy)]
    # Orientation by frozen pair-specific tie-breaker (unlike label-order orientation).
    for i, j, _ in selected:
        if p['u_expose'][tick,i,j] < p['u_expose'][tick,j,i]:
            i,j = j,i
        yield i,j

def load_integrated():
    src = inspect.getsource(original.simulate)
    start = src.index('  for i in available:\n   i=int(i)')
    end = src.index('    listed+=1;seen[j]+=1;', start)
    replacement = ('  for i,j in opportunities(p, eligible, available, config, seen, t, '
                   "config.get('schedule_mode','legacy'), config.get('schedule_slots',1)):\n"
                   '    i=int(i);j=int(j)\n')
    # Preserve the original body of the process from `listed` onwards by deleting
    # exactly two nested loops. This must be checked by legacy regression.
    source = src[:start] + replacement + src[end:]
    ns = dict(vars(original)); ns['opportunities'] = opportunities
    exec(compile(source, 'esbm_original_simulate_schedule_adapter', 'exec'), ns)
    return ns['simulate']

simulate = load_integrated()

# Raw risk-set diagnostics can be checked without changing the simulator state.
def audit_pair_schedule(p, eligible, available, tick, mode):
    plan = list(opportunities(p, eligible, available, original.SCENARIOS['mixed_random'], np.zeros(original.N, dtype=int), tick, mode))
    seen = set()
    for i,j in plan:
        assert i != j and eligible[i,j] and i in available and j in available
        assert i not in seen and j not in seen, 'Disjointness violated'
        seen.update((i,j))
    assert len(plan) <= len(available)//2
    return {'pairs': len(plan),'events': plan,'participants': len(seen)}
