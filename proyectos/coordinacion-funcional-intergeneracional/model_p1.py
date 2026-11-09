"""P1 only intervention: scale local rarity feature by current k.

All other agent states, rewards, neighbor graph, communication and learning
rates inherit P0. See PROTOCOL_P1_SCALE.md for pre-registered comparison.
"""
import numpy as np
from model import Society

class ScaleAwareSociety(Society):
    def _choose(self,i:int,other_state:int,policy:str,learning:bool)->int:
        if policy not in ("learned","untrained"):
            return super()._choose(i,other_state,policy,learning)
        old=int(self.colors[i])
        if self.k==1:return 0
        freq=self.memory[i]/self.memory[i].sum()
        c=np.arange(self.k)
        features=np.column_stack((
            -self.k*freq,
            (c==old).astype(float),
            (c==other_state).astype(float)))
        scores=features@self.theta[i]
        if not learning or policy=="untrained":
            return int(np.argmax(scores))
        z=(scores-scores.max())/self.p.temp
        prob=np.exp(np.clip(z,-30,0))
        prob/=prob.sum()
        choice=int(self.action_rng.choice(self.k,p=prob))
        # Keep reward EXACTLY as P0: only the representation feature varies.
        reward=1-float(freq[choice])-self.p.switch_cost*(choice!=old)
        advantage=reward-self.reward_baseline[i]
        self.theta[i]=np.clip(
            self.theta[i]+self.p.lr*advantage*(features[choice]-prob@features)/self.p.temp,
            -8,8)
        self.reward_baseline[i]=.93*self.reward_baseline[i]+.07*reward
        return choice
