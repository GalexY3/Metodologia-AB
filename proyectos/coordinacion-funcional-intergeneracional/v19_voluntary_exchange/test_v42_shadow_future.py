"""Mathematical and physics-engine regression tests for V42's oracle."""
from __future__ import annotations
import unittest
from v42_shadow_future import V,GAMMA,analytical_delta,material_verification,mc_one
class TestV42(unittest.TestCase):
 def test_exact_material_paired_gifts(self):
  for cost in (.04,.12):
   r=material_verification(cost)
   self.assertAlmostEqual(r["cooperative_one_round_food"],.2+V-cost,places=6)
   self.assertAlmostEqual(r["extra_private_gain_from_defection"],cost,places=6)
   self.assertAlmostEqual(r["loss_of_one_reciprocal_recipient"],-V,places=6)
   self.assertTrue(r["no_other_bystanders_affected"])
 def test_known_single_round_is_defection(self):
  for cost in (.04,.12):
   self.assertAlmostEqual(analytical_delta(cost,0),-cost,places=10)
 def test_threshold_both_prices(self):
  self.assertLess(analytical_delta(.04,.20),0)
  self.assertGreater(analytical_delta(.04,.25),0)
  self.assertLess(analytical_delta(.12,.60),0)
  self.assertGreater(analytical_delta(.12,.75),0)
  self.assertGreater(V*GAMMA*.8,.12)
 def test_sampled_geometric_discount_matches_analytic(self):
  x=mc_one(.04,.8,20000,seed=42112026)
  self.assertTrue(x["within_4se"])
if __name__=="__main__":unittest.main()
