"""V30 bilateral voluntary contract conservation and consent invariants."""
import unittest,torch
from targeted_gifts import C
from v24_k4_joint import start4
from v30_consensual import contract_step,oracle_contract,OBSERVATIONS
class V30Contract(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  self.c=C(n=48,k=4,degree=6,topology='ring',batch=2,horizon=12,cost=.04,device='cpu')
 def test_mutual_oracle_full_coverage(self):
  self.assertAlmostEqual(oracle_contract(self.c)['food'],.88,places=5)
 def test_unmatched_proposal_never_charges_or_delivers(self):
  w=start4(self.c,711,'balanced')
  dst=w['graph'][None,:,:3].expand(self.c.batch,-1,-1)
  yes=torch.zeros(self.c.batch,self.c.n,3)
  yes[:,0,0]=1.
  reward,distinct=contract_step(self.c,w,dst,yes)
  self.assertTrue(torch.allclose(reward,torch.full_like(reward,.2)))
  self.assertEqual(float(distinct.sum()),0.)
  self.assertEqual(float(w['prev_gift'].sum()),0.)
 def test_two_opposing_offers_settle_and_cost_both(self):
  w=start4(self.c,711,'balanced')
  destination=torch.zeros(self.c.batch,self.c.n,3,dtype=torch.long)
  offers=torch.zeros(self.c.batch,self.c.n,3)
  destination[:,0,0]=1;destination[:,1,0]=0
  offers[:,0,0]=1;offers[:,1,0]=1
  reward,distinct=contract_step(self.c,w,destination,offers)
  self.assertAlmostEqual(float(distinct[:,0].mean()),1.)
  self.assertAlmostEqual(float(distinct[:,1].mean()),1.)
  self.assertAlmostEqual(float(reward[:,0].mean()),.2+.55/3-.04,places=6)
  self.assertAlmostEqual(float(reward[:,1].mean()),.2+.55/3-.04,places=6)
  self.assertEqual(float(w['prev_gift'].sum()),4.)
 def test_multiple_proposals_same_pair_only_one_contract(self):
  w=start4(self.c,711,'balanced')
  destination=torch.zeros(self.c.batch,self.c.n,3,dtype=torch.long)
  destination[:,0,:]=1;destination[:,1,:]=0
  offers=torch.zeros(self.c.batch,self.c.n,3)
  offers[:,0,:]=1;offers[:,1,:]=1
  reward,distinct=contract_step(self.c,w,destination,offers)
  self.assertAlmostEqual(float(reward[:,0].mean()),.2+.55/3-.04,places=6)
  self.assertAlmostEqual(float(reward[:,1].mean()),.2+.55/3-.04,places=6)
if __name__=='__main__':unittest.main()
