"""Private donor memory correctly decays without injecting cooperation."""
import unittest,torch
from targeted_gifts import C,create,step
class Memory(unittest.TestCase):
 def test_decay_and_no_unearned_food(self):
  c=C(n=24,k=2,degree=2,batch=2,horizon=3,
      device='cpu',memory_decay=.85)
  w=create(c,100)
  chosen=w['graph'][None,:,0].expand(2,-1).clone()
  donate=torch.zeros(2,24);donate[:,0]=1
  chosen[:,0]=1
  step(c,w,chosen,donate)
  first=w['trust'].clone()
  self.assertEqual(float(w['incoming'][:,1,:].sum()),2.)
  step(c,w,chosen,torch.zeros_like(donate))
  self.assertEqual(float(w['incoming'].sum()),0.)
  self.assertTrue(torch.allclose(w['trust'],first*.85))
  self.assertAlmostEqual(float(w['lastfood'].mean()),.2,places=6)
 def test_zero_decay_preserves_one_step(self):
  c=C(n=24,k=2,degree=2,batch=2,horizon=3,device='cpu',memory_decay=0)
  w=create(c,100)
  chosen=w['graph'][None,:,0].expand(2,-1).clone()
  donate=torch.zeros(2,24);donate[:,0]=1
  chosen[:,0]=1
  step(c,w,chosen,donate);step(c,w,chosen,torch.zeros_like(donate))
  self.assertEqual(float(w['trust'].sum()),0.)
if __name__=='__main__':unittest.main(verbosity=2)
