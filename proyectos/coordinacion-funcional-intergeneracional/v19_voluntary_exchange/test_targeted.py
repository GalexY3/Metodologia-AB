"""Directed gift test: costly own action, recipient effect, individual gradients."""
import unittest,torch
from targeted_gifts import C,create,step,PrivateGiftActor,simulate
class Tests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_no_direct_personal_benefit_and_real_externality(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=4,horizon=4,cost=.12)
  zero=create(c,71);other=create(c,71)
  dest=zero['graph'][None,:,0].expand(c.batch,-1).clone()
  gifts=torch.zeros(c.batch,c.n);gifts[:,0]=1.
  dest[:,0]=1
  a=step(c,zero,dest,gifts)
  b=step(c,other,dest,torch.zeros_like(gifts))
  self.assertAlmostEqual(float((a-b)[:,0].mean()),-.12,places=6)
  self.assertAlmostEqual(float((a-b)[:,1].mean()),+.8,places=6)
  self.assertAlmostEqual(float((a-b)[:,23].mean()),0,places=6)
  self.assertGreater(float((a-b).sum(1).mean()),0)
 def test_gift_to_different_neighbor_changes_recipient(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=2,horizon=2)
  w=create(c,71)
  dest=w['graph'][None,:,0].expand(c.batch,-1).clone()
  gifts=torch.zeros(c.batch,c.n);gifts[:,0]=1
  dest[:,0]=23
  step(c,w,dest,gifts)
  self.assertEqual(float(w['incoming'][0,23].sum()),1.)
  self.assertEqual(float(w['incoming'][0,1].sum()),0.)
 def test_gradient_private(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=3,horizon=3)
  w=create(c,71)
  a=PrivateGiftActor(24,12,8)
  _,_,lp,_=a.act(c,w)
  (-lp[:,0].mean()).backward()
  for name,p in a.named_parameters():
   self.assertLess(float(p.grad[1:].abs().max()),1e-9,name)
 def test_ablations_and_baselines_complete(self):
  c=C(n=24,k=2,degree=2,device='cpu',batch=3,horizon=3)
  a=PrivateGiftActor(24,12,8)
  for mode in ('normal','no_social','scramble'):
   x=simulate(c,a,71,mode)
   self.assertEqual(len(x[1]),3)
  for b in ('always','never','random','titfortat'):
   x=simulate(c,a,71,baseline=b)
   self.assertEqual(len(x[1]),0)
if __name__=='__main__':unittest.main(verbosity=2)
