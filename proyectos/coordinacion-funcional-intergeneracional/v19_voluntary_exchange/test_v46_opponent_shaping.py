"""V46 Markov chain, individual-gradient and opponent-shaping regression."""
from __future__ import annotations
import unittest,numpy as np,torch
from v46_exact_opponent_shaping import (components,expected,gradients,
   measurements,N,B,V,C,GAMMA)
class V46Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2);torch.manual_seed(460043)
  self.logits=torch.nn.Parameter(torch.randn(N,5,dtype=torch.double)*.15)
 def test_joint_probabilities_sum_to_one(self):
  _,_,p,pj,first,trans=components(self.logits[::2],self.logits[1::2])
  self.assertTrue(torch.allclose(first.sum(1),torch.ones(24,dtype=torch.double),atol=1e-13))
  self.assertTrue(torch.allclose(trans.sum(2),torch.ones(24,4,dtype=torch.double),atol=1e-13))
 def test_exact_vs_independent_numpy_bellman_recursion(self):
  logit=self.logits.detach().numpy()
  a=1/(1+np.exp(-logit[0]));b=1/(1+np.exp(-logit[1]))
  beta=.95*GAMMA
  def recursion(T):
   def reward_and_transition(x,y):
    return B+V*y-C*x,np.array([(1-x)*(1-y),(1-x)*y,x*(1-y),x*y])
   future=np.zeros(4)
   for _ in range(T-1):
    next=np.zeros(4)
    for s,(i,j) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
     src=1+i*2+j
     swapped=1+j*2+i
     value,p=reward_and_transition(a[src],b[swapped])
     next[s]=value+beta*p.dot(future)
    future=next
   value,p=reward_and_transition(a[0],b[0])
   return value+beta*p.dot(future)
  for horizon in (2,3,5,13,48):
   actual=float(expected(self.logits[::2],self.logits[1::2],
     q=.95,horizon=horizon)[0].detach())
   self.assertAlmostEqual(actual,recursion(horizon),places=9)
 def test_private_nl_and_alpha0_are_identical(self):
  naive=gradients(self.logits,.95,'NL',0)
  assert naive.shape==(N,5)
  imitated=gradients(self.logits,.95,'LOLA',0)
  self.assertTrue(torch.allclose(naive,imitated,atol=1e-12))
  own=self.logits[::2];partner=self.logits[1::2]
  direct=torch.autograd.grad(expected(own,partner,q=.95).sum(),own)[0]
  self.assertTrue(torch.allclose(naive[::2],direct,atol=1e-12))
 def test_private_gradient_scalar_finite_difference(self):
  g=gradients(self.logits,.95,'NL',0)
  target=(0,1)
  eps=1e-4
  data=self.logits.detach().clone()
  plus=data.clone();minus=data.clone()
  plus[target]+=eps;minus[target]-=eps
  score_plus=float(expected(plus[0:1],plus[1:2],q=.95)[0])
  score_minus=float(expected(minus[0:1],minus[1:2],q=.95)[0])
  self.assertAlmostEqual(float(g[target]),(score_plus-score_minus)/(2*eps),places=6)
 def test_opponent_shaping_nonzero_second_order(self):
  direct=gradients(self.logits,.95,'NL',0)
  aware=gradients(self.logits,.95,'LOLA',5)
  look=gradients(self.logits,.95,'LOOK',5)
  self.assertTrue(torch.isfinite(aware).all())
  self.assertGreater(float((aware-direct).abs().max()),1e-7)
  self.assertGreater(float((aware-look).abs().max()),1e-7)
 def test_direct_private_cost_at_zero_future(self):
  for q in (.2,.95):
   zeros=torch.zeros(24,5)
   expected_delta=expected(zeros,zeros,q=q,force_first=1.)-expected(
      zeros,zeros,q=q,force_first=0.)
   self.assertTrue(torch.allclose(expected_delta,torch.full((24,),-C),atol=1e-6))
 def test_public_welfare_not_used_for_gradient(self):
  # NL gradients must equal gradient of own J, not summed joint welfare.
  ours=gradients(self.logits,.95,'NL',0)
  even=self.logits[::2];odd=self.logits[1::2]
  full=expected(even,odd,q=.95)+expected(odd,even,q=.95)
  welfare_grad=torch.autograd.grad(full.sum(),even)[0]
  self.assertGreater(float((welfare_grad-ours[::2]).abs().max()),1e-5)
if __name__=='__main__':unittest.main()
