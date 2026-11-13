"""V52 joint-learning private food, gradient and counterfactual invariants."""
import unittest,torch,numpy as np
from v51_endogenous_roles import PrivateRoleActor,context,load_frozen_gifts,N
from v52_joint_roles_gifts import rollout
class V52Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2);torch.manual_seed(52114)
  self.prof=PrivateRoleActor()
  self.gift=torch.nn.Parameter(torch.randn(N,5)*.05)
 def test_initial_joint_agents_private_parameter_shapes(self):
  self.assertEqual(self.gift.shape,(48,5))
  self.assertTrue(all(p.shape[0]==48 for p in self.prof.parameters()))
 def test_material_fixed_monolith_no_complement_payoff(self):
  c=context(3,"cpu",horizon=16)
  m,*_=rollout(c,self.gift,self.prof,998101,
    init="monolith",role_baseline="fixed")
  self.assertEqual(m["balanced_teams"],0)
  self.assertEqual(m["coverage"],0)
  self.assertEqual(m["full"],0)
  self.assertLess(m["food"],.21)
 def test_t0_forced_gift_own_private_exact_cost(self):
  c=context(3,"cpu",horizon=16)
  subjects=torch.tensor([0,1,2])
  a=rollout(c,self.gift,self.prof,998107,init="random",
   forced=1,subjects=subjects,return_own=True)
  b=rollout(c,self.gift,self.prof,998107,init="random",
   forced=0,subjects=subjects,return_own=True)
  instant=a[-1]-b[-1]
  self.assertTrue(torch.allclose(instant,torch.full((3,),-.04),atol=1e-6))
 def test_reinforce_has_private_donor_gradient(self):
  c=context(3,"cpu",horizon=16)
  m,r,lg,eg,lr,er,rt,*_=rollout(c,self.gift,self.prof,998109,init="mixed")
  advantages=r.detach()
  loss=-(lg*advantages).mean()-torch.stack(lr).mean()
  loss.backward()
  self.assertIsNotNone(self.gift.grad)
  self.assertTrue(torch.isfinite(self.gift.grad).all())
  self.assertTrue(any(p.grad is not None for p in self.prof.parameters()))
  self.assertTrue(torch.isfinite(torch.stack([p.grad.abs().sum() for p in self.prof.parameters()])).all())
 def test_strategic_prior_donates_more_than_scratch(self):
  prior=load_frozen_gifts("v47_Q95_LOLA20_s3111","cpu")
  c=context(3,"cpu",horizon=16)
  x,*_=rollout(c,self.gift,self.prof,998131,init="monolith")
  y,*_=rollout(c,prior,self.prof,998131,init="monolith")
  self.assertGreater(y["gift_slot_rate"],x["gift_slot_rate"]+.25)
if __name__=='__main__':unittest.main()
