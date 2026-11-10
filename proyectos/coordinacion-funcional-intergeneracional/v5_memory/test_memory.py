"""Adversarial isolation, memory and 10-color equivariance checks for V5."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v4_10states"))
import torch
from society10 import Society10,Config10,C,S
from agents_memory import MemoryAgents10
torch.set_num_threads(2)

def permute_observation(x,perm):
 y=x.clone()
 y[:,:,:C][:,:,perm]=x[:,:,:C]
 raw=x[:,:,C:C+S*C].reshape(*x.shape[:2],S,C)
 other=raw.clone();other[:,:,:,perm]=raw
 y[:,:,C:C+S*C]=other.reshape(*x.shape[:2],S*C)
 return y
def permute_payload(x,perm):
 y=x.clone()
 y[:,:,:,:C][:,:,:,perm]=x[:,:,:,:C]
 raw=x[:,:,:,C:C+S*C].reshape(*x.shape[:3],S,C)
 other=raw.clone();other[:,:,:,:,perm]=raw
 y[:,:,:,C:C+S*C]=other.reshape(*x.shape[:3],S*C)
 return y

class TestMemoryActors(unittest.TestCase):
 def setUp(self):
  torch.manual_seed(141)
  self.e=Society10(Config10(batch=3,seed=141))

 def test_candidate_actions_sized_ten(self):
  for mem in (1,8):
   net=MemoryAgents10(36,hidden=12,memory=mem)
   net.reset_memory(self.e.batch)
   o=self.e.observe()
   self.assertEqual(net.send_logits(o).shape,(3,36,51))
   sends,_,_=net.act_send(o)
   incoming,req,payload=self.e.deliveries(o,sends)
   self.assertEqual(net.choose_logits(o,incoming,req,payload,sends).shape,(3,36,10))

 def test_own_parameters_distinct_and_zero_cross_grad(self):
  net=MemoryAgents10(36,hidden=12,memory=8)
  net.reset_memory(self.e.batch)
  o=self.e.observe()
  s,lp,_=net.act_send(o)
  inc,req,payload=self.e.deliveries(o,s)
  ch,clp,_=net.act_choose(o,inc,req,payload,s)
  (-lp[:,0].sum()-clp[:,0].sum()).backward()
  for name,p in net.named_parameters():
   self.assertEqual(p.shape[0],36,name)
   if p.grad is not None:
    self.assertEqual(float(p.grad[1:].abs().sum()),0.0,name)

 def test_w8_retains_history_and_reset(self):
  net=MemoryAgents10(36,hidden=12,memory=8)
  net.reset_memory(3)
  o=self.e.observe()
  s,_,_=net.act_send(o)
  inc,req,pay=self.e.deliveries(o,s)
  initial=net.choose_logits(o,inc,req,pay,s,advance=False).detach().clone()
  net.choose_logits(o,inc,req,pay,s,advance=True)
  self.assertEqual(net.history.shape,(3,36,10,7,18))
  self.assertGreater(float(net.history.abs().sum()),0)
  after=net.choose_logits(o,inc,req,pay,s,advance=False)
  self.assertFalse(torch.allclose(initial,after))
  net.reset_memory(3)
  self.assertTrue((net.history==0).all())
  restored=net.choose_logits(o,inc,req,pay,s,advance=False)
  self.assertTrue(torch.allclose(initial,restored))

 def test_no_other_agent_raw_message_leak(self):
  net=MemoryAgents10(36,hidden=12,memory=8)
  net.reset_memory(3)
  o=self.e.observe()
  s=torch.zeros((3,36),dtype=torch.long)
  inc=torch.zeros((3,36,5),dtype=torch.bool)
  req=torch.zeros((3,36,5),dtype=torch.long)
  a=net.choose_logits(o,inc,req,torch.randn(3,36,5,o.shape[-1]),s,advance=False)
  b=net.choose_logits(o,inc,req,torch.randn(3,36,5,o.shape[-1])*100,s,advance=False)
  self.assertTrue(torch.allclose(a,b,atol=1e-6))

 def test_permutation_equivariance_with_memory(self):
  net=MemoryAgents10(36,hidden=12,memory=8)
  net.reset_memory(3)
  o=self.e.observe()
  s,_,_=net.act_send(o)
  inc,req,pay=self.e.deliveries(o,s)
  net.choose_logits(o,inc,req,pay,s,advance=True)
  perm=torch.randperm(10)
  o2=permute_observation(o,perm)
  pay2=permute_payload(pay,perm)
  req2=perm[req]
  s2=torch.where(s==0,s,1+((s-1)//C)*C+perm[(s-1).clamp(min=0)%C])
  # Color axis 2 in history, not the temporal axis
  hist=net.history.clone()
  log1=net.send_logits(o)
  c1=net.choose_logits(o,inc,req,pay,s,advance=False)
  net.history[:,:,perm,:,:]=hist
  log2=net.send_logits(o2)
  c2=net.choose_logits(o2,inc,req2,pay2,s2,advance=False)
  self.assertTrue(torch.allclose(log1[:,:,0],log2[:,:,0],atol=1e-5))
  self.assertTrue(torch.allclose(log1[:,:,1:].reshape(3,36,5,10),
                                 log2[:,:,1:].reshape(3,36,5,10)[:,:,:,perm],atol=1e-5))
  self.assertTrue(torch.allclose(c1,c2[:,:,perm],atol=1e-5))

 def test_requires_explicit_reset(self):
  net=MemoryAgents10(36,hidden=12,memory=8)
  with self.assertRaises(RuntimeError):
   net.send_logits(self.e.observe())
  net.reset_memory(3)
  self.assertTrue(torch.equal(net.history,torch.zeros_like(net.history)))

if __name__=="__main__":unittest.main()
