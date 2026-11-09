"""P0 — Decentralized functional coordination, k-variable agent-based model.

No globally observed population counts are passed to agents. Each undirected
communication edge forms at most one matched conversation per tick. Agent
policies observe one partner's current color and own discounted contact memory.
Designed to be auditable, not to imply sociological emergence without tests.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

N_DEFAULT=120
INITIAL_THETA=np.array([0.60,0.35,0.0],dtype=np.float64)

def make_ring(n:int,degree:int=4)->tuple[list[tuple[int,int]],list[tuple[int,...]]]:
    if degree!=4 or n<8:
        raise ValueError("P0 uses a 4-neighbor undirected ring with n>=8")
    neighbors=[set() for _ in range(n)]
    for i in range(n):
        for delta in (-2,-1,1,2):
            j=(i+delta)%n
            neighbors[i].add(j)
            neighbors[j].add(i)
    edges=sorted({(min(i,j),max(i,j)) for i in range(n) for j in neighbors[i]})
    assert all(len(a)==4 for a in neighbors)
    return edges,[tuple(sorted(v)) for v in neighbors]

def minimum_tv_discrete(n:int,k:int)->float:
    if k<1 or n<1 or k>n:
        raise ValueError("Need 1<=k<=n")
    q,rem=divmod(n,k)
    counts=[q+1 if i<rem else q for i in range(k)]
    return float(0.5*sum(abs(c/n-1/k) for c in counts))

@dataclass(frozen=True)
class Parameters:
    n:int=120
    memory_decay:float=.94
    lr:float=.35
    temp:float=.55
    switch_cost:float=.12
    stability_tv:float=.06
    stability_churn:float=.05
    stability_window:int=10
    init_majority:float=.70

class Society:
    def __init__(self,k:int,seed:int,params:Parameters=Parameters(),
                 theta:np.ndarray|None=None,initial_colors:np.ndarray|None=None):
        if k<1 or k>params.n:raise ValueError("Illegal number of functions")
        self.k=int(k);self.seed=int(seed);self.p=params;self.n=params.n
        self.rng=np.random.default_rng(seed)
        # Independent streams: different policies get the same per-tick
        # communication opportunities and initial colors for a given seed.
        self.match_rng=np.random.default_rng(np.random.SeedSequence([seed,1007]))
        self.action_rng=np.random.default_rng(np.random.SeedSequence([seed,2009]))
        self.edges,self.neighbors=make_ring(self.n)
        self.colors=self._initial_colors() if initial_colors is None else np.array(initial_colors,dtype=np.int32).copy()
        if len(self.colors)!=self.n or np.any(self.colors<0) or np.any(self.colors>=k):
            raise ValueError("Initial states must be among 0,...,k-1")
        if theta is None:
            self.theta=np.broadcast_to(INITIAL_THETA,(self.n,3)).copy()
            # Jitter shared across all comparisons by seed; not dependent on k.
            self.theta+=self.rng.normal(0,.03,size=(self.n,3))
        else:
            self.theta=np.array(theta,dtype=np.float64).copy()
        if self.theta.shape!=(self.n,3):raise ValueError("theta must be N x 3")
        self.initial_theta=self.theta.copy()
        self.memory=np.full((self.n,k),1/k,dtype=np.float64)
        self.reward_baseline=np.full(self.n,.70,dtype=np.float64)
        self.interactions_last=np.zeros(self.n,dtype=np.int8)
        self.t=0
        self.history:list[dict]=[]
        self.record(0,0)

    def _initial_colors(self)->np.ndarray:
        if self.k==1:return np.zeros(self.n,dtype=np.int32)
        majority=int(round(self.p.init_majority*self.n))
        states=np.concatenate([
            np.zeros(majority,dtype=np.int32),
            self.rng.integers(1,self.k,size=self.n-majority,dtype=np.int32)])
        self.rng.shuffle(states)
        return states

    def population_counts(self)->np.ndarray:
        """Evaluator-only global counts. Never called by decision policy."""
        return np.bincount(self.colors,minlength=self.k)

    def global_tv(self)->float:
        counts=self.population_counts()
        return float(.5*np.sum(np.abs(counts/self.n-1/self.k)))

    def local_richness(self)->float:
        denom=min(self.k,5)
        return float(np.mean([
            len({int(self.colors[i]),*(int(self.colors[j]) for j in self.neighbors[i])})/denom
            for i in range(self.n)]))

    def record(self,churn:float,matched_n:int)->dict:
        rec={"tick":self.t,"k":self.k,"tv":self.global_tv(),
             "churn":float(churn),"richness":self.local_richness(),
             "matched_agents":int(matched_n),
             "population_counts":self.population_counts().tolist()}
        self.history.append(rec)
        return rec

    def matching(self)->list[tuple[int,int]]:
        used=np.zeros(self.n,dtype=np.int8)
        matching=[]
        for e in self.match_rng.permutation(len(self.edges)):
            i,j=self.edges[int(e)]
            if used[i]==0 and used[j]==0:
                used[i]=used[j]=1
                matching.append((i,j))
        self.interactions_last=used
        return matching

    def _choose(self,i:int,other_state:int,policy:str,learning:bool)->int:
        old=int(self.colors[i])
        if self.k==1:return 0
        if policy=="stay":return old
        if policy=="copy":return other_state
        if policy=="random":return int(self.action_rng.integers(0,self.k))
        local_freq=self.memory[i]/self.memory[i].sum()
        ids=np.arange(self.k)
        features=np.column_stack((-local_freq,(ids==old).astype(float),(ids==other_state).astype(float)))
        if policy=="minority":
            scores=2.0*features[:,0]+.32*features[:,1]
            return int(np.argmax(scores))
        if policy not in ("learned","untrained"):
            raise ValueError("Unknown policy "+policy)
        # Untrained has the same θ prior as trained but never updates it.
        scores=features@self.theta[i]
        if not learning or policy=="untrained":
            # Deterministic local decision; stable ties favor the old color.
            return int(np.argmax(scores))
        prob=np.exp(np.clip((scores-np.max(scores))/self.p.temp,-30,0))
        prob/=prob.sum()
        choice=int(self.action_rng.choice(self.k,p=prob))
        # Local complementarity payoff: rarity among observed contacts, not
        # a reward based on the global target or global population counts.
        reward=1-float(local_freq[choice])-self.p.switch_cost*(choice!=old)
        advantage=reward-self.reward_baseline[i]
        grad=(features[choice]-(prob@features))/self.p.temp
        self.theta[i]=np.clip(self.theta[i]+self.p.lr*advantage*grad,-8,8)
        self.reward_baseline[i]=.93*self.reward_baseline[i]+.07*reward
        return choice

    def tick(self,policy:str="learned",learning:bool=False)->dict:
        pairs=self.matching()
        old=self.colors.copy()
        next_colors=old.copy()
        # Only the exchanged color enters memory, at most one contact/person/tick.
        for i,j in pairs:
            ci=int(old[i]);cj=int(old[j])
            self.memory[i]*=self.p.memory_decay
            self.memory[j]*=self.p.memory_decay
            self.memory[i,cj]+=1.
            self.memory[j,ci]+=1.
        # Evaluate all decisions from the same old snapshot (synchronous).
        for i,j in pairs:
            next_colors[i]=self._choose(i,int(old[j]),policy,learning and policy=="learned")
            next_colors[j]=self._choose(j,int(old[i]),policy,learning and policy=="learned")
        self.colors=next_colors
        self.t+=1
        return self.record(float(np.mean(old!=next_colors)),len(pairs)*2)

    def run(self,ticks:int,policy:str="learned",learning:bool=False)->dict:
        if ticks<1:raise ValueError("ticks must be positive")
        for _ in range(ticks):self.tick(policy,learning)
        records=self.history
        window=self.p.stability_window
        first=None
        for end in range(window,len(records)):
            recent=records[end-window+1:end+1]
            if all(x["tv"]<=self.p.stability_tv and x["churn"]<=self.p.stability_churn for x in recent):
                first=recent[0]["tick"]
                break
        tail=records[-window:]
        return {
            "seed":self.seed,"policy":policy,"k":self.k,"ticks":ticks,
            "initial_tv":records[0]["tv"],"final_tv":records[-1]["tv"],
            "tail_tv_mean":float(np.mean([r["tv"] for r in tail])),
            "tail_churn_mean":float(np.mean([r["churn"] for r in tail])),
            "tail_local_richness":float(np.mean([r["richness"] for r in tail])),
            "first_stable_tick":first,"stable_at_end":first is not None and all(
                x["tv"]<=self.p.stability_tv and x["churn"]<=self.p.stability_churn for x in tail),
            "communication_agents_max":max(r["matched_agents"] for r in records),
            "communication_cost_total":sum(r["matched_agents"] for r in records),
            "min_discrete_tv":minimum_tv_discrete(self.n,self.k),
            "colors_final":self.colors.tolist(),
        }

def train_individual_policies(seed:int,episodes_per_k:int=8,ticks:int=120,
                              p:Parameters=Parameters())->tuple[np.ndarray,list[dict]]:
    rng=np.random.default_rng(seed)
    theta=None;report=[]
    for episode in range(episodes_per_k*3):
        k=(2,3,4)[episode%3]
        e_seed=int(rng.integers(1,2**31-1))
        soc=Society(k,e_seed,p,theta=theta)
        result=soc.run(ticks,"learned",learning=True)
        theta=soc.theta.copy()
        report.append({"episode":episode,"k":k,"seed":e_seed,
                       "initial_tv":result["initial_tv"],
                       "final_tv":result["final_tv"],
                       "tail_tv_mean":result["tail_tv_mean"],
                       "tail_churn_mean":result["tail_churn_mean"],
                       "theta_mean":np.mean(theta,axis=0).tolist()})
    assert theta is not None and theta.shape==(p.n,3)
    return theta,report
