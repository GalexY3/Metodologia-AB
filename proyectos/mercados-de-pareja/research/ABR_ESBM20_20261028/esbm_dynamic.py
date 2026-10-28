"""ESBM dynamic synthetic experiment (AB-R N69 onwards). No empirical calibration.
Population gender labels F/M/X and self-reported attraction scopes same/other/all
are artificial compatibility choices, not real population frequencies. Any eligible pair
requires mutual scope. Exposure, unilateral proposal, response, active relationships,
and dissolution have distinct denominators. No claims about human outcomes.
"""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter
from pathlib import Path
import numpy as np
import networkx as nx

HERE=Path(__file__).resolve().parent
SEEDS=[101,211,307,401,503,601]
N=144; STEPS=16; K=7
SCENARIOS={
 "mixed_random":dict(compat="general",policy="random",same_pref=0,private=False,public=False,hazard_mult=1),
 "heterosexual_restricted":dict(compat="FM_only",policy="random",same_pref=0,private=False,public=False,hazard_mult=1),
 "institutional_segregation":dict(compat="general",policy="same_norm",same_pref=0,private=False,public=False,hazard_mult=1),
 "explicit_norm_preference":dict(compat="general",policy="random",same_pref=1.3,private=False,public=False,hazard_mult=1),
 "popularity_ranking":dict(compat="general",policy="popular",same_pref=0,private=False,public=False,hazard_mult=1),
 "visibility_balancing":dict(compat="general",policy="balance",same_pref=0,private=False,public=False,hazard_mult=1),
 "private_rejection_learning":dict(compat="general",policy="random",same_pref=0,private=True,public=False,hazard_mult=1),
 "public_rejection_signal":dict(compat="general",policy="random",same_pref=0,private=False,public=True,hazard_mult=1),
 "longer_partnerships":dict(compat="general",policy="random",same_pref=0,private=False,public=False,hazard_mult=.40),
 "shorter_partnerships":dict(compat="general",policy="random",same_pref=0,private=False,public=False,hazard_mult=1.75),
}

def sigmoid(v): return 1/(1+math.exp(-max(-25,min(25,float(v)))))
def gini(array):
 a=np.sort(np.asarray(array,dtype=float)); n=len(a)
 return float(2*np.dot(np.arange(1,n+1),a)/(n*a.sum())-(n+1)/n) if a.sum()>0 else 0.0

def people(seed):
 rng=np.random.default_rng(seed)
 genders=np.array(["F"]*60+["M"]*60+["X"]*24)
 genders=genders[rng.permutation(N)]
 scopes=np.array(["all"]*72+["same"]*36+["other"]*36)[rng.permutation(N)]
 norm=rng.integers(0,3,N)
 q=rng.random(N)
 age=rng.integers(19,51,N)
 # Each individual is equally exposed to the different synthetic scenarios from a shared seed.
 # Bernoulli shocks stable by time, sender, receiver; no RNG consumption by condition.
 u_send=rng.random((STEPS,N,N)); u_reply=rng.random((STEPS,N,N));
 u_hazard=rng.random((STEPS,N,N));
 u_expose=rng.random((STEPS,N,N));
 u_match=rng.random((STEPS,N,N));
 return dict(genders=genders,scopes=scopes,norm=norm,q=q,age=age,u_send=u_send,u_reply=u_reply,u_hazard=u_hazard,u_expose=u_expose,u_match=u_match)

def compatibility(p,mode):
 g=p['genders']; scope=p['scopes']; allowed=np.zeros((N,N),bool)
 for i in range(N):
  for j in range(i+1,N):
   if mode=='FM_only': valid= (g[i]=='F' and g[j]=='M') or (g[i]=='M' and g[j]=='F')
   else:
    ci=(scope[i]=='all' or (scope[i]=='same' and g[i]==g[j]) or (scope[i]=='other' and g[i]!=g[j]))
    cj=(scope[j]=='all' or (scope[j]=='same' and g[j]==g[i]) or (scope[j]=='other' and g[j]!=g[i]))
    valid=bool(ci and cj)
   allowed[i,j]=allowed[j,i]=valid
 return allowed

def simulate(seed, name, config):
 p=people(seed)
 eligible=compatibility(p,config['compat'])
 q=p['q']; norm=p['norm']; age=p['age'];u_send=p['u_send'];u_reply=p['u_reply'];uh=p['u_hazard']
 partner=np.full(N,-1,dtype=int)
 start=np.full(N,-1,dtype=int)
 seen=np.zeros(N,dtype=int)
 requests_received=np.zeros(N,dtype=int)
 approvals=np.zeros(N,dtype=int)
 public_score=np.zeros(N,dtype=float)
 private_bias=np.zeros(N,dtype=float)
 formed=0; dissolved=0; listed=0; proposals=0; requests_accepted=0
 sent_by_norm=np.zeros(3,int); received_by_norm=np.zeros(3,int)
 norm_exp=0; norm_exposure_denom=0
 new_norm=0; cohorts=[]; endings=[]; completed_duration=[]; samples=[]
 key_pairs=set()
 assert not np.any(np.diag(eligible))
 edges_all=int(np.triu(eligible,1).sum())
 for t in range(STEPS):
  # Dissolution happens at START of tick based on previous relationships, from same fixed shocks.
  for i in range(N):
   j=int(partner[i])
   if j<=i:continue
   h=min(.90, (.12+.065*(norm[i]!=norm[j])+.004*abs(int(age[i])-int(age[j])))*config['hazard_mult'])
   if uh[t,i,j]<h:
    duration=t-int(start[i]); completed_duration.append(duration)
    partner[i]=partner[j]=-1; start[i]=start[j]=-1; dissolved+=1
  available=np.flatnonzero(partner<0)
  active_set=set(map(int,available))
  active_graph=eligible[np.ix_(available,available)]
  possible_edges=int(np.triu(active_graph,1).sum())
  impressions=[]; mutual=[]; tick_proposals=0
  for i in available:
   i=int(i)
   candidates=np.array([j for j in available if j!=i and eligible[i,j]],dtype=int)
   if not len(candidates):continue
   kk=min(K,len(candidates))
   # Weighted-random Gumbel top-k without replacement, fixed shocks by sender,target,t.
   # Equivalent transformation -log(-log(U)) gives Gumbel(0,1).
   scores=-np.log(-np.log(np.clip(p['u_expose'][t,i,candidates],1e-12,1-1e-12)))
   if config['policy']=='same_norm': scores+=1.7*(norm[candidates]==norm[i])
   elif config['policy']=='popular': scores+=3.5*(q[candidates]-.5)
   elif config['policy']=='balance': scores+=-1.4*np.log1p(seen[candidates])
   picks=candidates[np.argsort(scores)[-kk:]]
   for j in picks:
    j=int(j)
    listed+=1;seen[j]+=1;received_by_norm[norm[j]]+=1
    norm_exposure_denom+=1;norm_exp+=int(norm[i]==norm[j])
    impressions.append((i,j))
    same=int(norm[i]==norm[j]);gap=abs(int(age[i])-int(age[j]))
    send_util=-.85+1.6*(q[j]-.5)+config['same_pref']*same-.012*gap+private_bias[i]
    if u_send[t,i,j]>=sigmoid(send_util):continue
    proposals+=1;tick_proposals+=1;approvals[i]+=1;requests_received[j]+=1;sent_by_norm[norm[i]]+=1
    rep_effect=public_score[i] if config['public'] else 0
    reply_util=-.85+1.6*(q[i]-.5)+config['same_pref']*same-.012*gap+rep_effect
    if u_reply[t,j,i]<sigmoid(reply_util):
     requests_accepted+=1;mutual.append((i,j))
    else:
     if config['private']:private_bias[i]=min(.80,private_bias[i]+.08)
     if config['public']:public_score[i]=max(-1.8,public_score[i]-.08)
  # Undirected relation candidate edges: duplicates collapsed, all had explicit two approvals.
  ug=nx.Graph();ug.add_nodes_from(map(int,available))
  for i,j in mutual:
   x,y=sorted((i,j));
   if x==y:raise AssertionError('self match')
   ug.add_edge(x,y,weight=1.0+1e-4*float(p['u_match'][t,x,y]))
  pairs=nx.algorithms.matching.max_weight_matching(ug,maxcardinality=True,weight='weight')
  for i,j in pairs:
   i=int(i);j=int(j)
   assert partner[i]==-1 and partner[j]==-1 and eligible[i,j]
   assert ug.has_edge(i,j)
   partner[i]=j;partner[j]=i;start[i]=start[j]=t
   formed+=1; new_norm+=int(norm[i]==norm[j]);key_pairs.add(tuple(sorted((i,j))))
  assert all((partner[i]==-1 or partner[partner[i]]==i) for i in range(N))
  ongoing=int((partner>=0).sum()//2)
  samples.append(dict(t=t,singles=len(available),risk_edges=possible_edges,impressions=len(impressions),proposals=tick_proposals,reciprocals=len(mutual),new_pairs=len(pairs),active_pairs=ongoing))
 # Aggregate partner-stage outputs without implying single connection = stable relationship.
 active_pairs=int((partner>=0).sum()//2)
 censored_durations=[STEPS-int(start[i]) for i in range(N) if partner[i]>i]
 ever_seen=seen>0
 nonselectable=np.sum(~eligible.any(axis=1))
 result={
  'seed':seed,'scenario':name,'n_agents':N,'time_steps':STEPS,
  'gender_distribution':dict(Counter(p['genders'])),'scope_distribution':dict(Counter(p['scopes'])),
  'possible_compatibility_pairs':edges_all,'agents_no_eligible_partner':int(nonselectable),
  'total_impressions':int(listed),'total_proposals':int(proposals),'total_positive_responses':int(requests_accepted),
  'total_relationships_formed':int(formed),'total_dissolutions':int(dissolved),
  'active_partnerships_end':active_pairs,'active_agent_share_end':float(2*active_pairs/N),
  'never_displayed_receivers':int((~ever_seen).sum()),'receiver_impression_gini':gini(seen),
  'group_same_exposure':float(norm_exp/norm_exposure_denom) if norm_exposure_denom else None,
  'group_same_new_couples':float(new_norm/formed) if formed else None,
  'duration_completed_mean':float(np.mean(completed_duration)) if completed_duration else None,
  'duration_completed_n':len(completed_duration),'right_censored_count':len(censored_durations),
  'mean_active_pairs':float(np.mean([x['active_pairs'] for x in samples])),
  'final_private_aspiration_bias_mean':float(np.mean(private_bias)),
  'final_public_reputation_penalty_mean':float(np.mean(public_score)),
  'impression_count_by_gender':{key:int(seen[p['genders']==key].sum()) for key in ['F','M','X']},
  'active_share_by_gender':{key:float(np.mean(partner[p['genders']==key]>=0)) for key in ['F','M','X']},
  'track':samples,
 }
 assert formed-dissolved==active_pairs,(name,seed,formed,dissolved,active_pairs)
 assert len(key_pairs)<=formed
 assert result['total_positive_responses']<=result['total_proposals']<=result['total_impressions']
 assert all(x['active_pairs']<=N//2 and x['new_pairs']<=x['reciprocals'] for x in samples)
 assert sum(result['impression_count_by_gender'].values())==listed
 return result

METRICS=['total_impressions','total_proposals','total_positive_responses','total_relationships_formed','total_dissolutions','active_partnerships_end','active_agent_share_end','mean_active_pairs','never_displayed_receivers','receiver_impression_gini','group_same_exposure','group_same_new_couples','duration_completed_mean','final_private_aspiration_bias_mean','final_public_reputation_penalty_mean']

def run():
 rows=[]
 for seed in SEEDS:
  for name,config in SCENARIOS.items():rows.append(simulate(seed,name,config))
 summaries=[]
 for name in SCENARIOS:
  r=[x for x in rows if x['scenario']==name]
  item={'scenario':name,'seeds':len(r)}
  for metric in METRICS:
   v=[x[metric] for x in r if x[metric] is not None]
   item[metric+'_mean']=round(float(np.mean(v)),6) if v else None
   item[metric+'_sd']=round(float(np.std(v,ddof=1)),6) if len(v)>1 else None
  item['compatible_pairs_mean']=float(np.mean([x['possible_compatibility_pairs'] for x in r]))
  item['agents_no_eligible_mean']=float(np.mean([x['agents_no_eligible_partner'] for x in r]))
  summaries.append(item)
 # paired by seeds with same agents and shocks; does not establish human causal mechanisms
 checks={'seeds':len(SEEDS),'scenarios':len(SCENARIOS),'runs':len(rows),'unique_scenario_seed':len({(x['seed'],x['scenario']) for x in rows})==len(rows),
         'all_have_positive_impressions':all(x['total_impressions']>0 for x in rows),
         'all_match_balances':all(x['total_relationships_formed']-x['total_dissolutions']==x['active_partnerships_end'] for x in rows),
         'all_reciprocals_le_proposals':all(x['total_positive_responses']<=x['total_proposals'] for x in rows),
         'no_person_level_data':True,'no_empirical_calibration':True,
         'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 for path,data in [('RUNS.json',rows),('SUMMARY.json',summaries),('QA.json',checks)]:
  (HERE/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with (HERE/'SUMMARY.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,summaries[0].keys());w.writeheader();w.writerows(summaries)
 print(json.dumps(checks,indent=2))
 for r in summaries:print(f"{r['scenario']:29s} active={r['active_agent_share_end_mean']:.3f} formed={r['total_relationships_formed_mean']:.1f} dissol={r['total_dissolutions_mean']:.1f} gini={r['receiver_impression_gini_mean']:.3f} within-group={r['group_same_new_couples_mean']:.3f}")

if __name__=='__main__':run()
