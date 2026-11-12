"""Invariant checks for the k=4, N=48 and N=120 extension."""
import unittest,torch
from targeted_gifts import C,PrivateGiftActor,step
from v24_k4_joint import PrivateOccupationK,start4,adjacent_potential,roll
class TestK4(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(211)
  self.c=C(n=48,k=4,degree=6,topology="ring",
           batch=4,horizon=8,cost=.12,device="cpu")
  self.actor=PrivateOccupationK(48,4,8)
  self.gifts=PrivateGiftActor(48,8,8.)
 def test_monolith_roles_equal_within_world(self):
  w=start4(self.c,761,"monolith")
  self.assertTrue(bool((w["roles"]==w["roles"][:,0,None]).all()))
  self.assertEqual(adjacent_potential(self.c,w),0.)
 def test_balanced_ring_can_access_all_three_missing_goods(self):
  w=start4(self.c,761,"balanced")
  self.assertAlmostEqual(adjacent_potential(self.c,w),1.)
 def test_full_four_professions_only_when_receiving_all_others(self):
  w=start4(self.c,761,"balanced")
  target=w["graph"][None,:,:].expand(self.c.batch,-1,-1)[:,:,0]
  z=torch.zeros(self.c.batch,self.c.n)
  reward=step(self.c,w,target,z)
  self.assertAlmostEqual(float(w["full"].sum()),0.)
  self.assertAlmostEqual(float(w["cover"].sum()),0.)
  self.assertAlmostEqual(float(reward.mean()),.2,places=6)
 def test_actions_choose_categorical_label(self):
  w=start4(self.c,761,"random")
  roles,logp,en=self.actor.act(self.c,w)
  self.assertEqual(roles.shape,(self.c.batch,self.c.n))
  self.assertTrue(bool(((roles>=0)&(roles<4)).all()))
  self.assertEqual(tuple(logp.shape),(4,48))
 def test_private_parameters_receive_separate_gradients(self):
  w=start4(self.c,761,"random")
  _,lp,_=self.actor.act(self.c,w)
  lp[:,3].sum().backward()
  self.assertGreater(float(self.actor.W.grad[3].abs().sum()),0)
  self.assertEqual(float(self.actor.W.grad[:3].abs().sum()),0.)
 def test_roll_horizon_and_role_interval(self):
  m,r,gl,ge,rl,re,rt=roll(self.c,self.gifts,self.actor,
      761,init="mixed",interval=8)
  self.assertEqual(r.shape,(8,4,48))
  self.assertEqual(rt,[0])
  self.assertEqual(len(gl),8)
  self.assertEqual(len(rl),1)
  self.assertGreaterEqual(m["potential_coverage"],0.)
  self.assertLessEqual(m["potential_coverage"],1.)
 def test_n120_same_protocol(self):
  c=C(n=120,k=4,degree=6,topology="ring",
        batch=2,horizon=8,cost=.12,device="cpu")
  w=start4(c,761,"balanced")
  self.assertEqual(w["roles"].shape,(2,120))
  self.assertAlmostEqual(adjacent_potential(c,w),1.)
if __name__=="__main__":unittest.main()
