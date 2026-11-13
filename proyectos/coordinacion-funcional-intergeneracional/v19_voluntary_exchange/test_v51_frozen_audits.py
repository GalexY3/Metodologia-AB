"""V51 heldout role-reassignment audits and terminal metrics."""
from __future__ import annotations
import unittest,torch,numpy as np
from v51_endogenous_roles import PrivateRoleActor,context,scenario,load_frozen_gifts,N,G
from v51_frozen_audits import rearrange_roles,SEEDS,CONDITIONS,INITS,METRICS
class V51AuditTests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(5101)
  self.actor=PrivateRoleActor()
  self.gifts=load_frozen_gifts("v47_Q95_LOLA20_s3111","cpu")
 def test_relocation_only_permutes_private_roles_in_each_team(self):
  initial=[p.detach().clone() for p in self.actor.parameters()]
  moved=rearrange_roles(self.actor,SEEDS[0])
  self.assertTrue(any(not torch.equal(a,b) for a,b in zip(initial,moved.parameters())))
  for a,b in zip(initial,moved.parameters()):
   self.assertTrue(torch.equal(a.sort(0).values,b.detach().sort(0).values))
   for group in range(G):
    i=4*group
    self.assertTrue(torch.equal(a[i:i+4].sort(0).values,
      b.detach()[i:i+4].sort(0).values))
  for a,b in zip(initial,self.actor.parameters()):
   self.assertTrue(torch.equal(a,b.detach()))
 def test_terminal_measures_and_unmodified_material(self):
  c=context(3,"cpu",horizon=16)
  row,*_=scenario(c,self.gifts,self.actor,SEEDS[0],init="monolith")
  for k in METRICS:self.assertIn(k,row)
  self.assertTrue(0<=row["terminal_balanced_teams"]<=1)
  self.assertTrue(0<=row["terminal_full"]<=1)
  self.assertTrue(row["food"]>=0)
  fixed,*_=scenario(c,self.gifts,self.actor,SEEDS[0],init="monolith",baseline="fixed")
  self.assertEqual(fixed["terminal_balanced_teams"],0)
  self.assertEqual(fixed["terminal_full"],0)
 def test_reserved_seeds_controls(self):
  self.assertEqual(len(SEEDS),6)
  self.assertEqual(len(set(SEEDS)),6)
  self.assertEqual(len(CONDITIONS),6)
  self.assertEqual(set(INITS),{"monolith","random"})
if __name__=='__main__':unittest.main()
