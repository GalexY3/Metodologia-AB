"""V26 reproducibility tests of retained donor memory and reward invariance."""
import unittest,torch
from dataclasses import replace
from targeted_gifts import C
from v24_k4_joint import start4
from v25_multi_capacity import step_multi

class TestRelationalMemory(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  self.c=C(n=48,k=4,degree=6,topology="ring",batch=2,
     horizon=8,cost=.04,device="cpu",memory_decay=.94)
 def setup_world(self,c):
  w=start4(c,711,"balanced")
  dest=torch.zeros(c.batch,c.n,3,dtype=torch.long)
  dest[:,:,0]=w["graph"][None,:,0].expand(c.batch,-1)
  gifts=torch.zeros(c.batch,c.n,3)
  gifts[:,:,0]=1.
  step_multi(c,w,dest,gifts)
  initial=w["trust"].clone()
  return w,dest,initial
 def test_high_memory_persists_private_help_after_silence(self):
  w,targets,previous=self.setup_world(self.c)
  self.assertGreater(float(previous.sum()),0)
  z=torch.zeros(self.c.batch,self.c.n,3)
  step_multi(self.c,w,targets,z)
  self.assertTrue(torch.allclose(w["trust"],previous*.94))
  step_multi(self.c,w,targets,z)
  self.assertTrue(torch.allclose(w["trust"],previous*.94**2))
 def test_zero_memory_is_v25_original(self):
  c=replace(self.c,memory_decay=0.)
  w,d,past=self.setup_world(c)
  step_multi(c,w,d,torch.zeros(c.batch,c.n,3))
  self.assertEqual(float(w["trust"].sum()),0.)
 def test_memory_changes_observation_not_immediate_material_reward(self):
  c0=replace(self.c,memory_decay=0.)
  a=start4(self.c,711,"balanced");b=start4(c0,711,"balanced")
  dest=torch.arange(self.c.n)[None,:,None].expand(self.c.batch,-1,3).clone()
  dest[:,:,0]=a["graph"][None,:,0]
  z=torch.zeros(self.c.batch,self.c.n,3);z[:,:,0]=1.
  ra,_=step_multi(self.c,a,dest,z)
  rb,_=step_multi(c0,b,dest,z)
  self.assertTrue(torch.equal(ra,rb))
if __name__=="__main__":unittest.main()
