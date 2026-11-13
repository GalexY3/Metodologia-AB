"""V43 release-blocking tests for deterministic original-rollout parity.

Any fixed-horizon visible-clock difference in rewards or sampled actions
would confound interpretation. Dead worlds may not contribute gradients.
"""
from __future__ import annotations
import unittest,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK
from v25_multi_capacity import roll as original_roll
from v43_random_horizon import roll as new_roll
class V43Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(430011)
  self.gift=PrivateGiftActor(48,12,8.)
  self.role=PrivateOccupationK(48,4,12)
  self.c=C(n=48,k=4,degree=6,topology="ring",batch=3,
    horizon=16,cost=.04,device="cpu")
 def test_fixed_visible_exact_physical_and_action_parity(self):
  torch.manual_seed(41116)
  a,ra,lga,ega,lra,era,rta=original_roll(
   self.c,self.gift,self.role,seed=1234,init="mixed",
   interval=8,move_cost=.015,social=True)
  torch.manual_seed(41116)
  b,rb,lgb,egb,lrb,erb,rtb=new_roll(
   self.c,self.gift,self.role,seed=1234,init="mixed",
   interval=8,move_cost=.015,q=1.,hidden_clock=False)
  self.assertTrue(torch.equal(ra,rb))
  self.assertEqual(rta,rtb)
  for x,y in ((lga,lgb),(ega,egb),(lra,lrb),(era,erb)):
   self.assertEqual(len(x),len(y))
   for xx,yy in zip(x,y):self.assertTrue(torch.equal(xx,yy))
  self.assertAlmostEqual(a["food"],b["food"],places=6)
  self.assertAlmostEqual(a["gifts_per_person"],b["gifts_per_person"],places=6)
 def test_terminated_worlds_never_revive_and_do_not_reward(self):
  torch.manual_seed(432112)
  m,reward,lg,eg,lr,er,rt=new_roll(
   self.c,self.gift,self.role,seed=1234,init="mixed",
   interval=8,q=.25,hidden_clock=True)
  self.assertTrue(1<=m["mean_alive_rounds"]<16)
  active=(reward.abs().sum(2)>0)
  self.assertTrue(bool((active[1:]<=active[:-1]).all()))
  for t in range(16):
   hidden=~active[t]
   if bool(hidden.any()):
    self.assertEqual(float(reward[t,hidden].abs().sum()),0)
    self.assertEqual(float(lg[t][hidden].detach().abs().sum()),0)
    self.assertEqual(float(eg[t][hidden].detach().abs().sum()),0)
 def test_always_alive_expected_active_agent_rounds(self):
  torch.manual_seed(432112)
  m,*_=new_roll(self.c,self.gift,self.role,seed=1234,q=1.,hidden_clock=True)
  self.assertEqual(m["mean_alive_rounds"],16)
  self.assertEqual(m["last_round_survival"],1.)
if __name__=="__main__":unittest.main()
