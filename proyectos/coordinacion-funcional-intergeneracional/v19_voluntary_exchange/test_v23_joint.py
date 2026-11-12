"""Invariants and intervention checks for V23 simultaneous cold start."""
import unittest
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v22_occupations import PrivateOccupationActor
from v23_joint_cold import roll
from v23_joint_audit import forced

class TestJointColdStart(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(123)
  self.c=C(n=24,k=2,degree=2,topology="ring",batch=3,
           horizon=8,cost=.12,gamma=.995,device="cpu")
  self.donor=PrivateGiftActor(24,8,8.)
  self.role=PrivateOccupationActor(24,8)
 def test_two_fresh_separate_parameter_sets(self):
  self.assertNotEqual(self.donor.target_W.data_ptr(),self.role.W.data_ptr())
  self.assertFalse(bool(torch.equal(self.donor.target_W[0],self.donor.target_W[1])))
  self.assertFalse(bool(torch.equal(self.role.W[0],self.role.W[1])))
 def test_all_routines_collect_correct_logprob_dimensions(self):
  metrics,rewards,lg,eg,lr,er,times=roll(self.c,self.donor,self.role,
      seed=722,init="mixed",interval=8)
  self.assertEqual(tuple(rewards.shape),(8,3,24))
  self.assertEqual(tuple(torch.stack(lg).shape),(8,3,24))
  self.assertEqual(tuple(torch.stack(lr).shape),(1,3,24))
  self.assertEqual(times,[0])
  self.assertGreater(metrics["switches_per_agent"],0.)
 def test_direct_person_cost_is_exactly_self_borne(self):
  results=[]
  for cond in (1,0):
   results.append(forced(self.c,self.donor,self.role,seed=722,
       init="monolith",mode="normal",condition=cond))
  self.assertTrue(np.allclose(results[0]["initial"]-
        results[1]["initial"],-.12,rtol=0,atol=1e-5))
 def test_coupled_counterfactual_is_deterministic(self):
  a=forced(self.c,self.donor,self.role,seed=722,
       init="random",mode="no_history",condition=1)
  b=forced(self.c,self.donor,self.role,seed=722,
       init="random",mode="no_history",condition=1)
  self.assertTrue(np.array_equal(a["total"],b["total"]))
 def test_one_individual_parameters_not_shared(self):
  w=__import__("v22_occupations").start(self.c,733,"random")
  _,lp,_=self.role.act(self.c,w)
  lp[:,3].sum().backward()
  self.assertGreater(float(self.role.W.grad[3].abs().sum()),0)
  self.assertEqual(float(self.role.W.grad[:3].abs().sum()),0.)
 def test_no_profession_change_baseline_monolith(self):
  with torch.no_grad():
   m,*_=roll(self.c,self.donor,self.role,seed=722,
         init="monolith",baseline="fixed",interval=8)
  self.assertEqual(m["complementary_links"],0.)
  self.assertEqual(m["balanced"],0.)
if __name__=="__main__":unittest.main()
