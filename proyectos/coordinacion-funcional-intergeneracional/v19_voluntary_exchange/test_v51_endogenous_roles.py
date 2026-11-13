"""V51 private role learning invariants and original four-role material law."""
from __future__ import annotations
import unittest,torch,numpy as np
from v51_endogenous_roles import (PrivateRoleActor,context,scenario,
 load_frozen_gifts,NEIGHBORS,REVERSE,N,G,K)
class V51Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(511199)
  self.actor=PrivateRoleActor()
  self.donor=load_frozen_gifts("v47_Q95_LOLA20_s3111","cpu")
 def test_clique_neighbors_are_three_and_reciprocal(self):
  self.assertEqual(NEIGHBORS.shape,(N,3))
  for i in range(N):
   self.assertEqual(len(set(NEIGHBORS[i])),3)
   for s,j in enumerate(NEIGHBORS[i]):
    self.assertEqual(NEIGHBORS[j,REVERSE[i,s]],i)
    self.assertEqual(i//4,j//4)
 def test_parameters_private_for_each_agent(self):
  for p in self.actor.parameters():
   self.assertEqual(p.shape[0],N)
 def test_unchanged_professions_monolith_never_complete(self):
  c=context(batch=3,device="cpu",horizon=16)
  measure,*_=scenario(c,self.donor,self.actor,997101,init="monolith",baseline="fixed")
  self.assertEqual(measure["balanced_teams"],0)
  self.assertEqual(measure["full"],0)
  self.assertEqual(measure["coverage"],0)
  self.assertLess(measure["food"],.21)
 def test_fixed_policy_role_sampling_reproducible(self):
  c=context(batch=3,device="cpu",horizon=16)
  a,*_=scenario(c,self.donor,self.actor,997107,init="random")
  b,*_=scenario(c,self.donor,self.actor,997107,init="random")
  self.assertEqual(a,b)
 def test_probabilities_of_choice_normalized(self):
  x=torch.randint(K,(2,N))
  f=torch.full((2,N),.2)
  s=torch.zeros_like(f)
  l=self.actor.logits(x,torch.as_tensor(NEIGHBORS),f,s,0)
  self.assertTrue(torch.allclose(torch.softmax(l,-1).sum(-1),
   torch.ones(2,N),atol=1e-6))
if __name__=="__main__":unittest.main()
