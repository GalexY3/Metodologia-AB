import unittest
from dataclasses import replace
import torch
from v12 import Config,World,IndividualAgent,food,metrics,graph,rollout,train_step,evaluate

class TestVillage(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
 def test_optimal_arbitrary_labels(self):
  for n,k,m in ((60,2,10),(60,3,20),(60,5,30),(120,6,40),(324,12,50)):
   for chosen in (list(range(k)),list(range(m-k,m))):
    jobs=torch.tensor([[j for lab in chosen for j in [lab]*(n//k)]])
    v,ct=food(jobs,m,k)
    self.assertTrue(torch.allclose(v,torch.ones_like(v)))
    res=metrics(jobs,v,ct,k)
    self.assertAlmostEqual(res['d'],0,places=6)
    self.assertEqual(res['exact'],1)
 def test_initial_random_not_optimal(self):
  cfg=Config(n=60,m=30,k=5,batch=24)
  w=World(cfg,9)
  self.assertGreater(metrics(w.jobs,w.food,w.counts,cfg.k)['d'],.1)
 def test_proposal_gradients_independent(self):
  cfg=Config(n=60,m=20,k=4,batch=8,communication=True)
  e=World(cfg,3)
  net=IndividualAgent(cfg.n)
  net.reset()
  _,lp,_=net.act(e)
  (-lp[:,0].sum()).backward()
  for param in net.parameters():
   self.assertIsNotNone(param.grad)
   self.assertEqual(float(param.grad[1:].abs().max()),0)
 def test_network_all_label_lengths(self):
  model=IndividualAgent(60)
  self.assertEqual(sum(p.numel() for p in model.parameters())//60,128)
  for m,k in ((10,2),(20,4),(30,5),(50,6)):
   c=Config(n=60,m=m,k=k,batch=4,communication=True,public=True)
   e=World(c,32)
   model.reset()
   nxt,lp,en=model.act(e)
   self.assertEqual(nxt.shape,(4,60))
   self.assertTrue(bool(((nxt>=0)&(nxt<m)).all()))
   self.assertTrue(bool(torch.isfinite(lp).all()))
 def test_local_info_but_not_global_histogram(self):
  c=Config(n=60,m=20,k=4,batch=4)
  e=World(c,12)
  a=e.local()[0,0].clone()
  remote=next(j for j in range(1,c.n) if j not in e.adj[0].tolist())
  e.jobs[0,remote]=(e.jobs[0,remote]+1)%c.m
  self.assertTrue(torch.equal(a,e.local()[0,0]))
 def test_k_hidden_from_actor_inputs(self):
  a=World(Config(n=60,m=10,k=2,batch=4),555)
  b=World(Config(n=60,m=10,k=5,batch=4),555)
  self.assertTrue(torch.equal(a.jobs,b.jobs))
  self.assertTrue(torch.equal(a.local(),b.local()))
  self.assertGreater(float((a.food-b.food).abs().sum()),0)
 def test_no_messages_control(self):
  c=Config(n=60,m=10,k=2,batch=5,communication=False)
  net=IndividualAgent(60)
  d=evaluate(net,c,seed=34,batch=5,horizon=4)
  self.assertEqual(d['final']['worlds'],5)
 def test_different_k_learning_step(self):
  net=IndividualAgent(60)
  opt=torch.optim.Adam(net.parameters(),lr=.005)
  for k in (2,4):
   c=Config(n=60,m=20,k=k,batch=6,horizon=5,communication=True,public=True,alpha=.1)
   result=train_step(net,opt,c,seed=22+k)
   self.assertTrue(result['loss']==result['loss'])
 def test_graph_degree(self):
  for n,degree in ((60,2),(60,5),(60,8),(324,5)):
   for topology in ('ring','rewired'):
    adj=graph(n,degree,topology,7)
    for i in range(n):
     self.assertEqual(len(set(adj[i].tolist())),degree)
     for j in adj[i]:self.assertIn(i,adj[j])
 def test_trap_local_stability(self):
  # N60 k2, all one profession. One worker switches alone; her reward falls.
  c=Config(n=60,m=20,k=2,batch=1,init='trap')
  e=World(c,22)
  self.assertAlmostEqual(float(e.food[0,0]),.5)
  next=e.jobs.clone(); next[0,0]=(next[0,0]+1)%c.m
  v,_=food(next,c.m,c.k)
  self.assertAlmostEqual(float(v[0,0]),1/30)

if __name__=='__main__':unittest.main(verbosity=2)
