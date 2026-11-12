"""V29 invariant and information-correction tests."""
import unittest
from dataclasses import replace
import copy,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
from v29_train import actual_sent_neighbor,precise_step,PreciseGiftActor

class TestV29(unittest.TestCase):
 def setUp(self):
  torch.manual_seed(2911)
  torch.set_num_threads(2)
  self.c=C(n=48,k=4,degree=6,topology="ring",batch=3,horizon=8,cost=.04,device="cpu")
  self.w=start4(self.c,211,"random")
  self.dests=self.w["graph"][None,:,[0,1,2]].expand(self.c.batch,-1,-1).clone()
  self.gifts=torch.zeros(self.c.batch,self.c.n,3)
 def clone(self,w):
  return {k:(v.clone() if isinstance(v,torch.Tensor) else v) for k,v in w.items()}
 def test_gifts_slot_two_are_remembered(self):
  self.gifts[:,:,2]=1
  flags=actual_sent_neighbor(self.w,self.dests,self.gifts)
  self.assertEqual(tuple(flags.shape),(3,48,6))
  self.assertTrue(torch.equal(flags[:,:,2],torch.ones(3,48)))
  self.assertEqual(float(flags[:,:,:2].sum()),0.)
 def test_target_slot_without_gift_is_not_memory(self):
  flags=actual_sent_neighbor(self.w,self.dests,self.gifts)
  self.assertEqual(float(flags.sum()),0.)
  self.assertTrue(bool((self.dests[:,:,0]>=0).all()))
 def test_material_reward_unchanged_by_memory_correction(self):
  self.gifts[:,:,2]=1
  original=self.clone(self.w)
  corrected=self.clone(self.w)
  before,dist1=step_multi(self.c,original,self.dests,self.gifts)
  after,dist2=precise_step(self.c,corrected,self.dests,self.gifts)
  self.assertTrue(torch.equal(before,after))
  self.assertTrue(torch.equal(dist1,dist2))
  for k in original:
   if isinstance(original[k],torch.Tensor):self.assertTrue(torch.equal(original[k],corrected[k]),k)
  self.assertEqual(float(corrected["prev_donated_slots"][:,:,2].mean()),1.)
 def test_policy_shapes_and_independent_private_params(self):
  actor=PreciseGiftActor(48,8,8.)
  _,give,lp,ent=actor.act(self.c,self.w)
  self.assertEqual(tuple(give.shape),(3,48))
  self.assertEqual(tuple(lp.shape),(3,48))
  self.assertEqual(tuple(ent.shape),(3,48))
  self.assertFalse(bool(torch.equal(actor.target_W[0],actor.target_W[1])))
 def test_degree_four_still_has_three_neighbor_roles(self):
  c=replace(self.c,degree=4)
  w=start4(c,2911,"balanced")
  from v24_k4_joint import adjacent_potential
  self.assertAlmostEqual(adjacent_potential(c,w),1.0)
if __name__=="__main__":unittest.main()
