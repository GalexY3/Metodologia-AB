"""V22 invariants: purely private occupational parameters, roles and baselines."""
import unittest,torch
from targeted_gifts import C,PrivateGiftActor
from v22_occupations import start,PrivateOccupationActor,rollout
class TestV22(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  self.c=C(n=24,k=2,degree=2,topology="ring",batch=6,horizon=8,device="cpu")
 def test_monolith_is_monolith(self):
  w=start(self.c,1881,"monolith")
  self.assertTrue(bool((w["roles"]==w["roles"][:,0,None]).all()))
  self.assertEqual(tuple(w["roles"].shape),(6,24))
 def test_random_has_valid_roles(self):
  w=start(self.c,1881,"random")
  self.assertTrue(bool(((w["roles"]==0)|(w["roles"]==1)).all()))
 def test_fixed_baseline_cannot_organize_monolith(self):
  gift=PrivateGiftActor(24,8)
  with torch.no_grad():
   data,*_=rollout(self.c,gift,None,seed=91,init="monolith",
                   baseline="fixed",role_interval=8)
  self.assertEqual(data["opposite_links"],0.)
  self.assertEqual(data["exactly_balanced"],0.)
  self.assertAlmostEqual(data["mean_switches_per_agent"],0.)
 def test_alternating_is_balanced_in_ring(self):
  gift=PrivateGiftActor(24,8)
  with torch.no_grad():
   data,*_=rollout(self.c,gift,None,seed=91,init="alternating",
                   baseline="fixed",role_interval=8)
  self.assertEqual(data["opposite_links"],1.)
  self.assertEqual(data["exactly_balanced"],1.)
 def test_occupation_private_parameters_not_shared(self):
  actor=PrivateOccupationActor(24,8)
  w=start(self.c,91,"monolith")
  switch,lp,entropy=actor.act(self.c,w)
  lp[:,0].sum().backward()
  self.assertGreater(float(actor.W.grad[0].abs().sum()),0)
  self.assertEqual(float(actor.W.grad[1:].abs().sum()),0.)
 def test_switch_is_binary(self):
  actor=PrivateOccupationActor(24,8)
  w=start(self.c,91,"random")
  move,*_=actor.act(self.c,w)
  self.assertTrue(bool(((move==0)|(move==1)).all()))
if __name__=="__main__":unittest.main()
