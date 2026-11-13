"""V43 frozen auditor verification of independent survival and counterfactuals."""
from __future__ import annotations
import unittest,numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK
from v43_frozen_audits import force_one,termination_generator
from v43_random_horizon import roll
class V43AuditTests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2);torch.manual_seed(431122)
  self.c=C(n=48,k=4,degree=6,topology='ring',
    batch=2,horizon=12,cost=.04,device='cpu')
  self.g=PrivateGiftActor(48,12,8.)
  self.r=PrivateOccupationK(48,4,12)
 def test_donation_t0_exact_own_cost_when_hazard(self):
  for q in (1.,.98,.4):
   a=force_one(self.c,self.g,self.r,970001,'monolith',1,q,True)
   b=force_one(self.c,self.g,self.r,970001,'monolith',0,q,True)
   self.assertTrue(np.allclose(a['initial']-b['initial'],-.04,atol=2e-5))
   self.assertTrue(np.allclose(a['total']-b['total'],
    (a['initial']-b['initial'])+(a['future']-b['future']),atol=2e-5))
 def test_private_hazard_pair_deterministic(self):
  args=(self.c,self.g,self.r,970007,'random',0,.98,False)
  a=force_one(*args)
  b=force_one(*args)
  for k in a:self.assertTrue(np.array_equal(a[k],b[k]))
 def test_survival_independent_of_role_baseline_draws(self):
  results=[]
  for cond in (None,'fixed','random_0.35'):
   torch.manual_seed(970001*73+41)
   metric,*_=roll(self.c,self.g,self.r,970001,
    q=.55,hidden_clock=True,role_baseline=cond,
    survival_generator=termination_generator(970001,'cpu'))
   results.append(metric['mean_alive_rounds'])
  self.assertEqual(results,[results[0]]*len(results))
if __name__=='__main__':unittest.main()
