"""V40 paired one-gift counterfactual private/social accounting tests."""
import unittest
from v40_marginal_wedge import paired
class TestV40MaterialCausality(unittest.TestCase):
 def test_unilateral_private_cost_and_recipient_gain_conserve_food(self):
  result=paired(970001,'v30_MUTUAL_C04_s3111',2,'cpu')
  x=result['by_regime']['unilateral']
  self.assertAlmostEqual(x['own_private'],-.04,places=5)
  self.assertAlmostEqual(x['net_social_total'],
    x['own_private']+x['targeted_recipient_gain'],places=5)
  self.assertGreater(x['targeted_recipient_gain'],0)
  self.assertGreaterEqual(x['useful_fraction'],0)
  self.assertLessEqual(x['useful_fraction'],1)
 def test_replay_reproducible_under_same_environment(self):
  a=paired(970007,'v30_MUTUAL_C04_s3111',2,'cpu')
  b=paired(970007,'v30_MUTUAL_C04_s3111',2,'cpu')
  self.assertEqual(a,b)
 def test_high_price_is_still_private_cost(self):
  a=paired(970001,'v31_N120_MUTUAL_C12_s3111',1,'cpu')
  x=a['by_regime']['unilateral']
  self.assertAlmostEqual(x['own_private'],-.12,places=5)
if __name__=='__main__':unittest.main()
