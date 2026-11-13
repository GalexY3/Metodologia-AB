"""V37 new cohort cohort-identity, frozen resident, and private-gradient tests."""
import unittest,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4
from v37_train import initial_cohort,replace_people,newcomer_indices,episode
class TestNewcohort(unittest.TestCase):
 def setUp(self):
  torch.manual_seed(3731)
  torch.set_num_threads(2)
  self.n=120;self.seed=3111
  self.spec=dict(n=120,k=4,hidden=8,init_scale=8.)
  self.donor=PrivateGiftActor(120,8,8.).requires_grad_(False)
  self.role=PrivateOccupationK(120,4,8).requires_grad_(False)
  self.newg,self.newr,self.ids=initial_cohort(self.donor,self.role,
    self.spec,'cpu',self.seed)
  self.mask=torch.zeros(self.n,dtype=torch.bool);self.mask[self.ids]=1
 def test_exactly_thirty_independently_private_newcomers(self):
  self.assertEqual(int(self.mask.sum()),30)
  self.assertTrue(torch.equal(self.ids,newcomer_indices(120,3111)))
  for old,new in ((self.donor,self.newg),(self.role,self.newr)):
   any_changed=False
   for k,v in old.named_parameters():
    now=dict(new.named_parameters())[k]
    self.assertTrue(torch.equal(v[~self.mask],now[~self.mask]),k)
    any_changed|=not torch.equal(v[self.mask],now[self.mask])
   self.assertTrue(any_changed)
 def test_shock_resets_only_expected_private_history(self):
  c=C(n=120,k=4,degree=6,topology='ring',
     batch=2,horizon=48,cost=.04,device='cpu')
  w=start4(c,2211,'random')
  w['trust'].fill_(1)
  group=replace_people(c,w,self.ids,2311)
  self.assertTrue(torch.equal(group,self.mask))
  touched=self.mask[w['graph']]
  self.assertEqual(float(w['trust'][:,touched].sum()),0.)
  self.assertTrue(torch.all(w['prev_gift'][:,self.ids]==0))
  self.assertTrue(torch.all(w['prev_recipient'][:,self.ids]==-1))
 def test_private_policy_gradient_confined_to_newcomers(self):
  c=C(n=120,k=4,degree=6,topology='ring',batch=2,horizon=48,
      cost=.04,device='cpu')
  r,gl,ge,rl,re,rt,m=episode(c,self.donor,self.role,
      self.newg,self.newr,self.ids,123456,init='monolith')
  self.assertEqual(tuple(r.shape),(24,2,120))
  self.assertEqual(rt,[8,16])
  private_loss=-torch.stack(gl)[:,:,self.ids].sum()
  self.newg.zero_grad()
  private_loss.backward()
  self.assertEqual(float(self.newg.gift_W.grad[~self.mask].abs().sum()),0.)
  self.assertGreater(float(self.newg.gift_W.grad[self.mask].abs().sum()),0.)
if __name__=='__main__':unittest.main()
