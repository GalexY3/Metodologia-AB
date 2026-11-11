"""Independent neural actors initialized toward exploratory recruiting policy.

This arm explicitly embeds a researcher-specified prior into network output
biases; it is NOT learning cooperation from scratch. All weights remain
distinct parameters per agent, updated individually by food REINFORCE.
"""
from __future__ import annotations
import torch,math
import neural_dual
import neural_pledge as p

class InitializedDual(neural_dual.DualNet):
 def __init__(self,n,h=16,rounds=8,quorum=True,features='lattice',
              scramble=False,gate=True):
  super().__init__(n,h,rounds,quorum,features,scramble,gate)
  with torch.no_grad():
   self.v.mul_(0.)
   self.bias[:,0]=0.0            # p(fission if above quota) = 0.50
   self.bias[:,1]=math.log(.65/.35) # p(join modal if underfull)=.65
   self.bias[:,2]=math.log(.98/.02) # p(advertise if underfull)=.98
if __name__=='__main__':
 args=p.parse()
 p.PledgeActor=InitializedDual
 p.main(args)
