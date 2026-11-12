"""V32 voluntary institutional mode choices preserve settlement endpoints."""
import unittest,torch
from targeted_gifts import C
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
from v30_consensual import contract_step,OBSERVATIONS
from v32_institution_choice import PrivateInstitutionActor,hybrid_step,roll
from targeted_gifts import PrivateGiftActor
from v24_k4_joint import PrivateOccupationK
class TestV32(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(987)
  self.c=C(n=48,k=4,degree=6,topology='ring',batch=3,horizon=8,
           cost=.04,device='cpu')
  self.original=start4(self.c,781,'random')
  self.targets=self.original['graph'][None,:,:3].expand(3,-1,-1).clone()
  self.offers=(torch.rand(3,48,3)<.65).float()
 def clone(self):
  return {k:(v.clone() if isinstance(v,torch.Tensor) else v)
          for k,v in self.original.items()}
 def test_unilateral_matches_original_rewards(self):
  left=self.clone();right=self.clone()
  a,_=step_multi(self.c,left,self.targets,self.offers)
  b,_=hybrid_step(self.c,right,self.targets,self.offers,torch.zeros(3,48))
  self.assertTrue(torch.equal(a,b))
  for key in ('lastfood','cover','full','prev_gift','incoming'):
   self.assertTrue(torch.equal(left[key],right[key]),key)
 def test_all_contract_is_same_v30_settlement(self):
  left=self.clone();right=self.clone()
  a,_=contract_step(self.c,left,self.targets,self.offers)
  b,_=hybrid_step(self.c,right,self.targets,self.offers,torch.ones(3,48))
  self.assertTrue(torch.equal(a,b))
  for key in ('lastfood','cover','full','prev_gift','incoming'):
   self.assertTrue(torch.equal(left[key],right[key]),key)
 def test_no_offers_baseline(self):
  w=self.clone()
  result,_=hybrid_step(self.c,w,self.targets,torch.zeros_like(self.offers),
                       torch.rand(3,48).round())
  self.assertAlmostEqual(float(result.mean()),.2,places=6)
 def test_mode_actor_private_gradients(self):
  actor=PrivateInstitutionActor(48,4,8,-2.)
  s,p,e=actor.act(self.c,self.original)
  self.assertEqual(s.shape,(3,48))
  p[:,0].sum().backward()
  self.assertGreater(float(actor.W.grad[0].abs().sum()),0.)
  self.assertEqual(float(actor.W.grad[1:].abs().sum()),0.)
 def test_joint_optimizable_shapes(self):
  d=PrivateGiftActor(48,8,8.)
  r=PrivateOccupationK(48,4,8)
  m=PrivateInstitutionActor(48,4,8)
  summary,returns,lg,eg,lr,er,rt,lm,em=roll(self.c,d,r,m,seed=17)
  self.assertEqual(tuple(returns.shape),(8,3,48))
  self.assertEqual(len(lm),8)
  self.assertEqual(len(lr),1)
  self.assertTrue(0<=summary['adoption']<=1)
if __name__=='__main__':unittest.main()
