"""V44 all-person one-step causal interventions and holdout separation."""
import unittest,torch,numpy as np
from v44_private_dyads import COST,PrivateDyadic,simulation
from v44_frozen_audits import force_one,SEEDS
class TestV44Causal(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2);torch.manual_seed(441134)
  self.actor=PrivateDyadic().eval().requires_grad_(False)
 def test_six_holdout_seeds_do_not_overlap_training_development(self):
  self.assertEqual(len(SEEDS),6)
  self.assertFalse(set(SEEDS)&{970001,970007,970009})
 def test_forced_gift_private_immediate_cost_is_exact(self):
  for q in (.2,.95):
   yes=force_one(self.actor,980101,2,q,True,'cpu',1)
   no=force_one(self.actor,980101,2,q,True,'cpu',0)
   self.assertTrue(np.allclose(yes['initial']-no['initial'],-COST,atol=2e-6))
   self.assertTrue(np.allclose(yes['total']-no['total'],
     yes['initial']-no['initial']+yes['future']-no['future'],atol=2e-5))
 def test_matched_rollouts_reproduce(self):
  x=force_one(self.actor,980107,2,.95,False,'cpu',1)
  y=force_one(self.actor,980107,2,.95,False,'cpu',1)
  for key in x:self.assertTrue(np.array_equal(x[key],y[key]))
if __name__=='__main__':unittest.main()
