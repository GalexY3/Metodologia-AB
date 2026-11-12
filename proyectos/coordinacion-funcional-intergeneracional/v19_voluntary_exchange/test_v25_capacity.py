"""Tests verifying resource accounting and feasible benchmark in V25."""
import unittest,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4
from v25_multi_capacity import oracle,step_multi,roll

class TestMultiCapacity(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(751)
  self.c=C(n=48,k=4,degree=6,topology="ring",
           batch=4,horizon=8,cost=.12,device="cpu")
 def test_oracle_perfect_assortment_with_three_units(self):
  result=oracle(self.c)
  self.assertAlmostEqual(result["full"],1.)
  self.assertAlmostEqual(result["cover"],1.)
  self.assertAlmostEqual(result["count"],3.)
  self.assertAlmostEqual(result["food"],.64,places=5)
 def test_oracle_scaled_cost_preserves_unit_budget(self):
  from dataclasses import replace
  result=oracle(replace(self.c,cost=.04))
  self.assertAlmostEqual(result["food"],.88,places=5)
 def test_duplicate_recipients_cannot_create_distinct_extra_goods(self):
  w=start4(self.c,1991,"random")
  torch.manual_seed(91)
  slots=torch.randint(self.c.degree,(self.c.batch,self.c.n,self.c.k-1))
  neighbor=w["graph"][None,:,:].expand(self.c.batch,-1,-1)
  dests=neighbor.gather(2,slots)
  gifts=(torch.rand(self.c.batch,self.c.n,self.c.k-1)<.5).float()
  _,distinct=step_multi(self.c,w,dests,gifts)
  self.assertTrue(bool((distinct.sum(1)<=gifts.sum((1,2))+1e-5).all()))
  self.assertTrue(bool((w["full"].sum(1)<=gifts.sum((1,2))/3+1e-5).all()))
 def test_no_donation_is_material_baseline(self):
  w=start4(self.c,1991,"random")
  zeros=torch.zeros(self.c.batch,self.c.n,3)
  target=w["graph"][None,:,:].expand(self.c.batch,-1,-1)[:,:,:3]
  x,_=step_multi(self.c,w,target,zeros)
  self.assertAlmostEqual(float(x.mean()),.2,places=6)
 def test_causal_one_of_three_slots_pays_exact_cost(self):
  import numpy as np
  from dataclasses import replace
  from v25_causal_audit import forced
  c=replace(self.c,batch=2)
  gift=PrivateGiftActor(48,8,8.)
  role=PrivateOccupationK(48,4,8)
  yes=forced(c,gift,role,801,"monolith","normal",1)
  no=forced(c,gift,role,801,"monolith","normal",0)
  self.assertTrue(np.allclose(yes["initial"]-no["initial"],
      -.12,rtol=0,atol=1e-5))
 def test_private_joint_policy_well_formed(self):
  gifts=PrivateGiftActor(48,8,8.)
  role=PrivateOccupationK(48,4,8)
  metrics,rewards,logs,ent,lr,er,rt=roll(self.c,gifts,role,seed=1991,
                                        init="mixed",interval=8)
  self.assertEqual(rewards.shape,(8,4,48))
  self.assertEqual(tuple(torch.stack(logs).shape),(8,4,48))
  self.assertEqual(rt,[0])
  self.assertGreaterEqual(metrics["gifts_per_person"],0)
  self.assertLessEqual(metrics["gifts_per_person"],3.)
  self.assertGreaterEqual(metrics["useful_delivery_ratio"],0)
  self.assertLessEqual(metrics["useful_delivery_ratio"],1.0001)
if __name__=="__main__":unittest.main()
