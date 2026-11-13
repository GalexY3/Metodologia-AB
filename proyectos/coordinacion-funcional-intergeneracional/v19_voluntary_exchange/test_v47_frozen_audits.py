"""V47 reproducibility and independent Monte Carlo audit tests."""
import unittest, numpy as np,torch
from v47_frozen_audits import PAIRING_SEEDS,ENV_SEEDS,MC_PAIRING_INDICES
from v46_frozen_audits import run_episode_population
from v46_exact_opponent_shaping import measurements,N
class V47FrozenTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_reserved_pairings_and_environments(self):
  self.assertEqual(len(PAIRING_SEEDS),12)
  self.assertEqual(len(set(PAIRING_SEEDS)),12)
  self.assertEqual(len(ENV_SEEDS),6)
  self.assertEqual(tuple(MC_PAIRING_INDICES),(0,6))
  for seed in PAIRING_SEEDS:
   self.assertEqual(sorted(np.random.default_rng(seed).permutation(N).tolist()),list(range(N)))
 def test_reassignment_does_not_modify_private_model(self):
  torch.manual_seed(47113)
  model=torch.randn(N,5,dtype=torch.double)*.5
  initial=model.clone()
  for seed in PAIRING_SEEDS:
   mapped=model[np.random.default_rng(seed).permutation(N)]
   self.assertTrue(torch.equal(model,initial))
   self.assertTrue(torch.equal(model.sort(0).values,mapped.sort(0).values))
 def test_independent_monte_carlo_matches_analytic_for_random_policies(self):
  torch.manual_seed(478)
  policy=torch.randn(N,5,dtype=torch.double)
  x=measurements(policy,q=.95)
  simulation=run_episode_population(policy,.95,ENV_SEEDS[0],1200)
  for field in ("food","mutual","gifts"):
   self.assertLess(abs(x[field]-simulation[field]),.015)
if __name__=="__main__":unittest.main()
