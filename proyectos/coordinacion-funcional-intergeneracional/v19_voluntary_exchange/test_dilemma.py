"""Formal unilateral public-goods dilemma: positive social externality, privately costly action."""
import unittest,torch
from exchange import Config,create_world,IndependentActors
import public_goods_dilemma as pg
class DilemmaTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_donor_cannot_consume_own_product(self):
  c=Config(n=60,k=2,degree=2,device='cpu',batch=2,horizon=4)
  w=create_world(c,17)
  roles=torch.zeros(2,60,dtype=torch.long)
  offers=torch.ones(2,60)
  pg.advance(c,w,roles,offers)
  self.assertTrue(bool((w['coverage']==.5).all()))
  self.assertTrue(bool((w['full']==0).all()))
 def test_donation_is_privately_costly_but_collectively_beneficial(self):
  c=Config(n=60,k=2,degree=2,device='cpu',batch=2,horizon=4)
  roles=torch.zeros(2,60,dtype=torch.long)
  roles[:,0]=1
  ones=torch.ones(2,60)
  w=create_world(c,17)
  baseline=pg.advance(c,w,roles,ones)
  w=create_world(c,17)
  defect=ones.clone();defect[:,0]=0
  counterfactual=pg.advance(c,w,roles,defect)
  gain=baseline-counterfactual
  self.assertAlmostEqual(float(gain[:,0].mean()),-c.cost,places=6)
  self.assertGreater(float(gain.sum(1).mean()),0)
  self.assertGreater(float(gain[:,1].mean()),0)
  self.assertGreater(float(gain[:,59].mean()),0)
  self.assertAlmostEqual(float(gain[:,2].mean()),0,places=6)
 def test_individual_gradient_has_no_cross_weight_leakage(self):
  c=Config(n=60,k=4,degree=8,device='cpu',batch=3,horizon=4)
  w=create_world(c,17)
  a=IndependentActors(60,12)
  _,_,lp,_=a.act(c,w)
  (-lp[:,0].mean()).backward()
  for key,p in a.named_parameters():
   self.assertLess(float(p.grad[1:].abs().max()),1e-9,key)
if __name__=='__main__':unittest.main(verbosity=2)
