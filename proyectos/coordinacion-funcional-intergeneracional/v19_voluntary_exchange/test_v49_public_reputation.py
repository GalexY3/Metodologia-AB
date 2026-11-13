"""V49 public reputation is identity-bound, matched and nonmaterial."""
import unittest,numpy as np
from v49_public_reputation import signals,run,ordinary,paired
from v48_within_episode_rewire import schedule,uniforms,batched_simulate
from v46_exact_opponent_shaping import N
class V49Tests(unittest.TestCase):
 def setUp(self):
  self.seed=995101
  self.params=np.random.default_rng(33).normal(0,.5,(N,5))
 def test_fixed_partner_public_equals_carry(self):
  for n in (2,7):
   a=ordinary(self.params,self.seed,n,0.,"carry")
   b=ordinary(self.params,self.seed,n,0.,"public")
   self.assertEqual(a,b)
 def test_carry_parity_with_v48_unchanged_payoff_engine(self):
  p,l=schedule(self.seed,3,.6)
  u=uniforms(self.seed,3)
  rr,nn=signals(self.seed,3)
  original=batched_simulate(self.params,p,l,u,"carry")
  updated=run(self.params,p,l,u,rr,nn,"carry")
  for k in ("food","gifts","mutual","distinct_partners"):
   self.assertAlmostEqual(original[k],updated[k],places=12)
 def test_one_gift_cost_exact_in_all_reputation_conditions(self):
  for mode in ("carry","public","scrambled","public_noise20"):
   r=paired(self.params,self.seed,2,1.,mode)
   self.assertAlmostEqual(r["immediate"],-.04,places=12)
   self.assertEqual(r,paired(self.params,self.seed,2,1.,mode))
 def test_public_and_scrambled_reputations_are_different_identity_maps(self):
  reporter,noise=signals(self.seed,4)
  self.assertEqual(reporter.shape,(48,4,N))
  self.assertTrue(np.all(reporter[:,:,:24]>=24))
  self.assertTrue(np.all(reporter[:,:,24:]<24))
  self.assertTrue(np.any(noise<.2))
if __name__=="__main__":unittest.main()
