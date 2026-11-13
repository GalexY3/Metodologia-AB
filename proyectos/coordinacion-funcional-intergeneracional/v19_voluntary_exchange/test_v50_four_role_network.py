"""V50 matching topology, own-causal intervention, and original V25 physical parity."""
import unittest,numpy as np,torch
from v50_four_role_network import (matching,action_draws,get_received,simulate,
 paired,ROLE,OTHER_ROLE,SLOT,N,M,S)
from targeted_gifts import C
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
class V50Tests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_three_complementary_neighbors_and_reciprocity_of_links(self):
  graph,alive=matching(996101,3,.25,steps=12)
  self.assertEqual(graph.shape,(12,3,N,3))
  self.assertTrue(np.all(ROLE[graph]==OTHER_ROLE[ROLE][None,None,:,:]))
  for t in range(12):
   for w in range(3):
    for i in range(N):
     for j in graph[t,w,i]:
      self.assertIn(i,graph[t,w,j])
  self.assertTrue(np.all(alive[1:]<=alive[:-1]))
 def test_material_parity_with_original_four_profession_engine(self):
  worlds=3
  graph,alive=matching(996107,worlds,0.,steps=1)
  partner=graph[0]
  actions=(action_draws(996107,worlds,1)[0]<.61).astype(np.int64)
  original=simulate(np.zeros((N,5)),graph,alive,
    action_draws(996107,worlds,1),"carry")
  # The one-turn policy uses p=.5, so use those actual Bernoulli draws.
  issued=(action_draws(996107,worlds,1)[0]<.5).astype(np.int64)
  net=get_received(issued,partner)
  expected=.2+.55*(net.sum(2)/3)+.25*(net.sum(2)==3)-.04*issued.sum(2)
  self.assertAlmostEqual(float(expected.mean()),original["food"],places=6)
  # V25 graph is common to the batch and shaped (N,degree).
  # Check each independently matched world against that original API.
  c=C(n=48,k=4,degree=6,topology="ring",batch=1,
   horizon=48,cost=.04,device="cpu")
  for w in range(worlds):
   state=start4(c,996107,"balanced")
   state["roles"]=torch.tensor(ROLE).view(1,N).clone()
   state["graph"]=torch.tensor(partner[w])
   state["trust"]=torch.zeros(1,N,S)
   state["incoming"]=torch.zeros(1,N,S)
   dest=torch.tensor(partner[w:w+1])
   gifts=torch.tensor(issued[w:w+1],dtype=torch.float)
   food,distinct=step_multi(c,state,dest,gifts)
   self.assertTrue(np.allclose(food.numpy(),expected[w:w+1],atol=2e-6))
 def test_full_cooperation_and_none_payoffs(self):
  graph,alive=matching(996101,2,0.,steps=1)
  self.assertTrue(np.all(alive))
  own=np.ones((2,N,3),dtype=np.int64)
  received=get_received(own,graph[0])
  self.assertTrue(np.all(received==1))
  self.assertAlmostEqual(.2+.55+.25-3*.04,.88,places=7)
 def test_force_first_gift_private_cost(self):
  policy=np.zeros((N,5))
  for rate in (0.,1.):
   for channel in ("carry","public","none"):
    z=paired(policy,996101,2,rate,channel)
    self.assertAlmostEqual(z["immediate"],-.04,places=9)
    self.assertEqual(z,paired(policy,996101,2,rate,channel))
 def test_fixed_partner_public_and_carry_are_physically_identical(self):
  policy=np.random.default_rng(33).normal(size=(N,5))
  g,a=matching(996101,3,0.)
  u=action_draws(996101,3)
  x=simulate(policy,g,a,u,"carry")
  y=simulate(policy,g,a,u,"public")
  for key in ("food","gifts_per_person","full","coverage"):
   self.assertAlmostEqual(x[key],y[key],places=10)
if __name__=="__main__":unittest.main()
