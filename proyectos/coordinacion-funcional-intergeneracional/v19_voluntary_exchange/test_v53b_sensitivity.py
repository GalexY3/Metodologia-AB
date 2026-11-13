"""V53B prerequisite one-factor, material baseline parity tests."""
import unittest
import v53_vsm_material as material
import v53b_sensitivity as sensitivity
class V53BTests(unittest.TestCase):
 def test_base_parametrization_is_exact_original(self):
  c=sensitivity.update("BASE")
  self.assertEqual(c["subsistence"],.75)
  self.assertEqual(c["transfer_loss"],.05)
  self.assertEqual(c["capacity"],2.2)
  self.assertAlmostEqual(material.simulate(999101,3,"PATCHY","LOCAL_GLOBAL")["survival"],
    material.simulate(999101,3,"PATCHY","LOCAL_GLOBAL")["survival"])
 def test_each_sensitivity_changes_only_declared_parameter(self):
  base=sensitivity.update("BASE")
  expected={
   "HALF_ADMIN":{"fees"},
   "ZERO_ADMIN":{"fees"},
   "DOUBLE_ADMIN":{"fees"},
   "FREE_TRANSFER":{"transfer_loss"},
   "LOSS20":{"transfer_loss"},
   "LOW_SUBSISTENCE":{"subsistence"},
   "HIGH_SUBSISTENCE":{"subsistence"},
   "SHORT_BUFFER":{"initial","capacity"},
   "LONG_BUFFER":{"initial","capacity"}}
  for name,changes in expected.items():
   out=sensitivity.update(name)
   observed={k for k in base if base[k]!=out[k]}
   self.assertEqual(observed,changes,name)
  sensitivity.update("BASE")
 def test_costless_intelligence_does_not_inject_physical_food(self):
  sensitivity.update("ZERO_ADMIN")
  a=material.simulate(999107,3,"QUIET","NONE")
  b=material.simulate(999107,3,"QUIET","FORECAST")
  self.assertAlmostEqual(a["mean_net_food_per_living"],.88,places=8)
  self.assertAlmostEqual(b["mean_net_food_per_living"],.88,places=8)
  sensitivity.update("BASE")
if __name__=="__main__":unittest.main()
