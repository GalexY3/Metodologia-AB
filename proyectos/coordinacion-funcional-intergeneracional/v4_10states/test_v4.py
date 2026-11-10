"""Tests: any k labels among ten, equivalent global quota and private agents."""
import unittest,math
import torch
from society10 import C,S,SEND_DIM,Config10,Society10
from actors10 import IndependentActors10
torch.set_num_threads(2)

class V4Tests(unittest.TestCase):
 def setUp(self):
  torch.manual_seed(141)
  self.env=Society10(Config10(rows=6,cols=6,batch=3,seed=141))
  self.net=IndependentActors10(n=36,hidden=16)

 def test_any_four_labels_equal_quotas_exact(self):
  e=self.env;e.reset(k=4)
  x=torch.tensor([0]*9+[2]*9+[5]*9+[9]*9)
  e.colors[:]=x[torch.randperm(36)]
  e.D=e.tv()
  self.assertTrue(torch.allclose(e.D,torch.zeros(3)))
  self.assertTrue(e.exact().all())
  # A fixed "colors 0..3" target would reject this correct solution.
  self.assertEqual(set(e.colors[0].tolist()),{0,2,5,9})

 def test_extra_fifth_state_is_penalized(self):
  e=self.env;e.reset(k=4)
  x=torch.tensor([0]*8+[2]*9+[5]*9+[9]*9+[7])
  e.colors[:]=x
  self.assertFalse(e.exact().any())
  self.assertGreater(float(e.tv()[0]),0)

 def test_random_ten_is_far_from_target(self):
  e=Society10(Config10(rows=6,cols=6,batch=256,seed=111))
  e.reset(k=4)
  self.assertGreater(float(e.tv().mean()),.2)
  self.assertEqual(int(e.exact().sum()),0)

 def test_k2_k3_k4_can_be_exact(self):
  e=self.env
  for k in (2,3,4):
   e.reset(k=k)
   x=torch.tensor(sum(([c]*(36//k) for c in (1,4,8,9)[:k]),[]))
   e.colors[:]=x
   self.assertTrue(e.exact().all())
   self.assertTrue(torch.allclose(e.tv(),torch.zeros(3),atol=1e-6))

 def test_no_message_self_color_change(self):
  e=self.env;e.reset(k=4)
  outgoing=torch.zeros((3,36),dtype=torch.long)
  obs=e.observe()
  incoming,requested,payload=e.deliveries(obs,outgoing)
  nxt=e.colors.clone()
  nxt[0,0]=(nxt[0,0]+1)%10
  z=e.step(outgoing,nxt,incoming,requested)
  self.assertEqual(float(z["messages"][0]),0)
  self.assertGreater(float(z["churn"][0]),0)

 def test_individual_only_gradients(self):
  e=self.env
  s,lp,_=self.net.act_send(e.observe())
  inc,req,payload=e.deliveries(e.observe(),s)
  c,clp,_=self.net.act_choose(e.observe(),inc,req,payload)
  (-lp[:,0].sum()-clp[:,0].sum()).backward()
  for name,p in self.net.named_parameters():
   if p.grad is not None:self.assertEqual(float(p.grad[1:].abs().sum()),0,name)

 def test_actor_cannot_see_global_histogram(self):
  # Only two scalar GLOBAL values D and delta, both identical across agents.
  obs=self.env.observe()
  self.assertEqual(obs.shape[-1],10+5*10+5+3)
  self.assertTrue(torch.equal(obs[:,0,-3:],obs[:,1,-3:]))
  send=torch.zeros((3,36),dtype=torch.long)
  inc,req,payload=self.env.deliveries(obs,send)
  self.assertEqual(tuple(self.env.step(send,self.env.colors.clone(),inc,req)["reward"].shape),(3,))

 def test_permutation_equivariance(self):
  e=self.env
  obs=e.observe()
  send,_,_=self.net.act_send(obs)
  inc,req,payload=e.deliveries(obs,send)
  perm=torch.randperm(10)
  o2=obs.clone()
  o2[:,:,:10][:,:,perm]=obs[:,:,:10]
  original_neighbors=obs[:,:,10:60].reshape(3,36,5,10)
  n2=original_neighbors.clone()
  n2[:,:,:,perm]=original_neighbors
  o2[:,:,10:60]=n2.reshape(3,36,50)
  payload2=payload.clone()
  payload2[:,:,:,:10][:,:,:,perm]=payload[:,:,:,:10]
  old=payload[:,:,:,10:60].reshape(3,36,5,5,10)
  new=old.clone();new[:,:,:,:,perm]=old
  payload2[:,:,:,10:60]=new.reshape(3,36,5,50)
  s1=self.net.send_logits(obs);s2=self.net.send_logits(o2)
  self.assertTrue(torch.allclose(s1[:,:,0],s2[:,:,0],atol=1e-6))
  self.assertTrue(torch.allclose(s1[:,:,1:].reshape(3,36,5,10),
                                s2[:,:,1:].reshape(3,36,5,10)[:,:,:,perm],atol=1e-5))
  q1=self.net.choose_logits(obs,inc,req,payload)
  q2=self.net.choose_logits(o2,inc,perm[req],payload2)
  self.assertTrue(torch.allclose(q1,q2[:,:,perm],atol=1e-5))

 def test_no_snapshot_leak_without_messages(self):
  e=self.env
  obs=e.observe()
  inc=torch.zeros((3,36,5),dtype=torch.bool)
  req=torch.zeros((3,36,5),dtype=torch.long)
  x=self.net.choose_logits(obs,inc,req,torch.randn(3,36,5,obs.shape[-1]))
  y=self.net.choose_logits(obs,inc,req,torch.randn(3,36,5,obs.shape[-1])*100)
  self.assertTrue(torch.allclose(x,y,atol=1e-6))

if __name__=="__main__":unittest.main()
