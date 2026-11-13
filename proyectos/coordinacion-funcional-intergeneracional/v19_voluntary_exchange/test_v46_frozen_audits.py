"""V46 frozen external simulation, policy-transfer and theory checks."""
from __future__ import annotations
import unittest,torch,numpy as np
from v46_exact_opponent_shaping import N,measurements,expected
from v46_frozen_audits import run_episode_population,SEEDS,PAIRING_SEEDS
class V46AuditTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_mc_independent_engine_matches_exact(self):
  torch.manual_seed(462113)
  logits=torch.randn(N,5,dtype=torch.double)*.5
  exact=measurements(logits,q=.95)
  sampled=run_episode_population(logits,.95,990101,worlds=1200)
  for k,target in (("food",exact["food"]),
    ("gifts",exact["gifts"]),("mutual",exact["mutual"])):
   self.assertAlmostEqual(sampled[k],target,delta=.015,msg=k)
 def test_tit_for_tat_pair_is_conditionally_profitable_under_long_horizon(self):
  theta=torch.full((N,5),-12.,dtype=torch.double)
  theta[:,0]=12.
  theta[:,2]=12.
  theta[:,4]=12.
  high=measurements(theta,q=.95)
  low=measurements(theta,q=.20)
  self.assertEqual(high["positive_agents"],48)
  self.assertEqual(low["positive_agents"],0)
  self.assertGreater(high["mutual"],.9)
  self.assertGreater(low["mutual"],.9)
 def test_partner_exchange_is_permutation_of_personal_policies(self):
  torch.manual_seed(4677)
  theta=torch.randn(N,5,dtype=torch.double)*.9
  p=np.random.default_rng(PAIRING_SEEDS[0]).permutation(N)
  rotated=theta[p]
  self.assertEqual(rotated.shape,theta.shape)
  self.assertTrue(torch.equal(rotated.sort(dim=0).values,theta.sort(dim=0).values))
  self.assertEqual(len(set(SEEDS)),6)
  self.assertFalse(set(SEEDS)&{970001,970007,970009,980101})
 def test_exact_intervention_has_direct_private_cost_if_memory_zero(self):
  for q in (.2,.95):
   zeros=torch.zeros(N//2,5,dtype=torch.double)
   a=expected(zeros,zeros,q=q,force_first=1.)
   b=expected(zeros,zeros,q=q,force_first=0.)
   self.assertTrue(torch.allclose(a-b,torch.full((24,),-.04,dtype=torch.double),atol=1e-8))
if __name__=='__main__':unittest.main()
