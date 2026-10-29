"""ESBM explicit encounter-event interface, branched N127–N146.
Exact historical ESBM is imported, SHA-guarded and unmodified.
Research simulation on artificial agents, no empirical calibration.
This file does not execute source patches, inspect or dynamic Python code.
"""
from __future__ import annotations
import hashlib
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
    if mode not in ('pair_max', 'pair_greedy', 'pair_budgeted_max', 'pair_sham', 'pair_norm_same', 'pair_norm_cross'):
        raise ValueError('Unknown institution: '+str(mode))
    if slots not in (1,2):
        raise ValueError('Only one or two appointment slots permitted by N117 contract')
    used_dyads=set()
    for slot in range(slots):
        # Reusing source shocks under deterministic shift is synthetic correlation, NOT new independent draws.
        u_slot=np.mod(p['u_expose'][tick]+slot*0.6180339887498948,1.0)
        # Same available population and eligible undirected edges for strong comparisons.
        # Weight = symmetric deterministic Gumbel shock, independent of actor ID ordering.
        # Actual fitted propensity/model of venue assignment is NOT claimed.
        edges = []
        for x, i in enumerate(available):
            for j in available[x+1:]:
                if not eligible[i, j] or (min(i,j),max(i,j)) in used_dyads:
                    continue
                a = float(u_slot[ i, j]); b = float(u_slot[ j, i])
                weight = -np.log(-np.log(np.clip(a, 1e-12, 1-1e-12))) + -np.log(-np.log(np.clip(b, 1e-12, 1-1e-12)))
                edges.append((i, j, weight))
        # Prospectively repaired N108: cap feasible candidate shortlists to top four
        # directed opportunity shocks per actor, then take the undirected union.
        # This restricts the graph; max matching is exact only within this shortlist.
        shortlist=set()
        for i in available:
            candidates=np.array([j for j in available if j!=i and eligible[i,j] and (min(i,j),max(i,j)) not in used_dyads],dtype=int)
            if not len(candidates):continue
            chosen=candidates[np.argsort(u_slot[i,candidates])[-min(4,len(candidates)):]]
            for j in chosen: shortlist.add((min(i,int(j)),max(i,int(j))))
        edges=[(i,j,w) for i,j,w in edges if (i,j) in shortlist]
        # New N112 institution: shift edge priority only after fixing candidate shortlist.
        # Group markers are artificial; this is not a claim about social norms in humans.
        if mode == 'pair_norm_same':
            edges=[(i,j,w+1.8*float(p['norm'][i]==p['norm'][j])) for i,j,w in edges]
        elif mode == 'pair_norm_cross':
            edges=[(i,j,w+1.8*float(p['norm'][i]!=p['norm'][j])) for i,j,w in edges]
        # pair_sham is exactly identical to pair_max (strong negative control).
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
        slot_agents=set()
        for i, j, _ in selected:
            assert i not in slot_agents and j not in slot_agents
            slot_agents.update((i,j))
            assert (min(i,j),max(i,j)) not in used_dyads
            used_dyads.add((min(i,j),max(i,j)))
            if u_slot[i,j] < u_slot[j,i]:
                i,j = j,i
            yield i,j

from collections import Counter
N=original.N
STEPS=original.STEPS
K=original.K
people=original.people
compatibility=original.compatibility
sigmoid=original.sigmoid
gini=original.gini

def simulate(seed, name, config, *, scheduler=None, trace=False, people_provider=None, compatibility_provider=None, population_size=None, steps=None, shock_policy="historical"):
 trace_rows=[]
 if shock_policy not in ("historical","symmetric_hazard","symmetric_pair"):raise ValueError("invalid shock_policy")
 p=(people_provider or people)(seed)
 eligible=(compatibility_provider or compatibility)(p,config['compat'])
 n_agents=int(population_size or len(p['genders']))
 step_count=int(steps or p['u_send'].shape[0])
 assert eligible.shape==(n_agents,n_agents)
 assert p['u_send'].shape[0]>=step_count
 q=p['q']; norm=p['norm']; age=p['age'];u_send=p['u_send'];u_reply=p['u_reply'];uh=p['u_hazard']
 partner=np.full(n_agents,-1,dtype=int)
 start=np.full(n_agents,-1,dtype=int)
 seen=np.zeros(n_agents,dtype=int)
 requests_received=np.zeros(n_agents,dtype=int)
 approvals=np.zeros(n_agents,dtype=int)
 public_score=np.zeros(n_agents,dtype=float)
 private_bias=np.zeros(n_agents,dtype=float)
 formed=0; dissolved=0; listed=0; proposals=0; requests_accepted=0
 sent_by_norm=np.zeros(3,int); received_by_norm=np.zeros(3,int)
 norm_exp=0; norm_exposure_denom=0
 new_norm=0; cohorts=[]; endings=[]; completed_duration=[]; samples=[]
 key_pairs=set()
 assert not np.any(np.diag(eligible))
 edges_all=int(np.triu(eligible,1).sum())
 for t in range(step_count):
  # Dissolution happens at START of tick based on previous relationships, from same fixed shocks.
  for i in range(n_agents):
   j=int(partner[i])
   if j<=i:continue
   h=min(.90, (.12+.065*(norm[i]!=norm[j])+.004*abs(int(age[i])-int(age[j])))*config['hazard_mult'])
   if (((uh[t,i,j]+uh[t,j,i])%1.0) if shock_policy in ("symmetric_hazard","symmetric_pair") else uh[t,i,j])<h:
    duration=t-int(start[i]); completed_duration.append(duration)
    if trace: trace_rows.append(dict(t=t,stage='dissolution',i=i,j=j))
    partner[i]=partner[j]=-1; start[i]=start[j]=-1; dissolved+=1
  available=np.flatnonzero(partner<0)
  active_set=set(map(int,available))
  active_graph=eligible[np.ix_(available,available)]
  possible_edges=int(np.triu(active_graph,1).sum())
  impressions=[]; mutual=[]; tick_proposals=0
  seen_meeting_pairs=set(); per_tick_encounters=np.zeros(n_agents,dtype=int)
  for i,j in (scheduler or opportunities)(p,eligible,available,config,seen,t,config.get('schedule_mode','legacy'),config.get('schedule_slots',1)):
    i=int(i);j=int(j)
    if not (0<=i<n_agents and 0<=j<n_agents and i!=j and i in active_set and j in active_set and eligible[i,j]):
     raise ValueError('Injected exposure outside eligible active risk set')
    if scheduler is not None or config.get('schedule_mode','legacy')!='legacy':
     dyad=(min(i,j),max(i,j))
     if dyad in seen_meeting_pairs:raise ValueError('Repeated dyad in one tick')
     if per_tick_encounters[i]>=config.get('schedule_slots',1) or per_tick_encounters[j]>=config.get('schedule_slots',1):
      raise ValueError('Per-actor meeting cap exceeded')
     seen_meeting_pairs.add(dyad);per_tick_encounters[i]+=1;per_tick_encounters[j]+=1
    if trace: trace_rows.append(dict(t=t,stage='exposure',i=i,j=j))
    listed+=1;seen[j]+=1;received_by_norm[norm[j]]+=1
    norm_exposure_denom+=1;norm_exp+=int(norm[i]==norm[j])
    impressions.append((i,j))
    same=int(norm[i]==norm[j]);gap=abs(int(age[i])-int(age[j]))
    send_util=-.85+1.6*(q[j]-.5)+config['same_pref']*same-.012*gap+private_bias[i]
    if u_send[t,i,j]>=sigmoid(send_util):continue
    if trace: trace_rows.append(dict(t=t,stage='proposal',i=i,j=j))
    proposals+=1;tick_proposals+=1;approvals[i]+=1;requests_received[j]+=1;sent_by_norm[norm[i]]+=1
    rep_effect=public_score[i] if config['public'] else 0
    reply_util=-.85+1.6*(q[i]-.5)+config['same_pref']*same-.012*gap+rep_effect
    if u_reply[t,j,i]<sigmoid(reply_util):
     if trace: trace_rows.append(dict(t=t,stage='positive_response',i=i,j=j))
     requests_accepted+=1;mutual.append((i,j))
    else:
     if trace: trace_rows.append(dict(t=t,stage='negative_response',i=i,j=j))
     if config['private']:private_bias[i]=min(.80,private_bias[i]+.08)
     if config['public']:public_score[i]=max(-1.8,public_score[i]-.08)
  # Undirected relation candidate edges: duplicates collapsed, all had explicit two approvals.
  ug=nx.Graph();ug.add_nodes_from(map(int,available))
  for i,j in mutual:
   x,y=sorted((i,j));
   if x==y:raise AssertionError('self match')
   w=(float((p['u_match'][t,x,y]+p['u_match'][t,y,x])%1.0) if shock_policy=='symmetric_pair' else float(p['u_match'][t,x,y]))
   ug.add_edge(x,y,weight=1.0+1e-4*w)
  pairs=nx.algorithms.matching.max_weight_matching(ug,maxcardinality=True,weight='weight')
  for i,j in pairs:
   i=int(i);j=int(j)
   assert partner[i]==-1 and partner[j]==-1 and eligible[i,j]
   assert ug.has_edge(i,j)
   partner[i]=j;partner[j]=i;start[i]=start[j]=t
   if trace: trace_rows.append(dict(t=t,stage='formation',i=i,j=j))
   formed+=1; new_norm+=int(norm[i]==norm[j]);key_pairs.add(tuple(sorted((i,j))))
  assert all((partner[i]==-1 or partner[partner[i]]==i) for i in range(n_agents))
  ongoing=int((partner>=0).sum()//2)
  samples.append(dict(t=t,singles=len(available),risk_edges=possible_edges,impressions=len(impressions),proposals=tick_proposals,reciprocals=len(mutual),new_pairs=len(pairs),active_pairs=ongoing))
 # Aggregate partner-stage outputs without implying single connection = stable relationship.
 active_pairs=int((partner>=0).sum()//2)
 censored_durations=[step_count-int(start[i]) for i in range(n_agents) if partner[i]>i]
 ever_seen=seen>0
 nonselectable=np.sum(~eligible.any(axis=1))
 result={
  'seed':seed,'scenario':name,'n_agents':n_agents,'time_steps':step_count,
  'gender_distribution':dict(Counter(p['genders'])),'scope_distribution':dict(Counter(p['scopes'])),
  'possible_compatibility_pairs':edges_all,'agents_no_eligible_partner':int(nonselectable),
  'total_impressions':int(listed),'total_proposals':int(proposals),'total_positive_responses':int(requests_accepted),
  'total_relationships_formed':int(formed),'total_dissolutions':int(dissolved),
  'active_partnerships_end':active_pairs,'active_agent_share_end':float(2*active_pairs/n_agents),
  'never_displayed_receivers':int((~ever_seen).sum()),'receiver_impression_gini':gini(seen),
  'group_same_exposure':float(norm_exp/norm_exposure_denom) if norm_exposure_denom else None,
  'group_same_new_couples':float(new_norm/formed) if formed else None,
  'duration_completed_mean':float(np.mean(completed_duration)) if completed_duration else None,
  'duration_completed_n':len(completed_duration),'right_censored_count':len(censored_durations),
  'mean_active_pairs':float(np.mean([x['active_pairs'] for x in samples])),
  'final_private_aspiration_bias_mean':float(np.mean(private_bias)),
  'final_public_reputation_penalty_mean':float(np.mean(public_score)),
  'impression_count_by_gender':{key:int(seen[p['genders']==key].sum()) for key in ['F','M','X']},
  'active_share_by_gender':{key:(float(np.mean(partner[p['genders']==key]>=0)) if np.any(p['genders']==key) else None) for key in ['F','M','X']},
  'track':samples,
 }
 assert formed-dissolved==active_pairs,(name,seed,formed,dissolved,active_pairs)
 assert len(key_pairs)<=formed
 assert result['total_positive_responses']<=result['total_proposals']<=result['total_impressions']
 assert all(x['active_pairs']<=n_agents//2 and x['new_pairs']<=x['reciprocals'] for x in samples)
 assert sum(result['impression_count_by_gender'].values())==listed
 if trace:
  result['events']=trace_rows
 return result

