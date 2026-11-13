"""V53 physics, resource conservation, reproducibility, and anti-cheating tests."""
from __future__ import annotations
import unittest,numpy as np
from v53_vsm_material import (N,TEAMS,K,T,material_food,shocks,
 rescue_local,schedule_global,simulate,ENVIRONMENTS,GOVERNANCE,TRANSFER_LOSS)
class TestV53(unittest.TestCase):
 def test_fully_complementary_gifts_give_original_food(self):
  alive=np.ones((2,TEAMS,K),dtype=bool)
  food,received=material_food(alive,np.zeros_like(alive))
  self.assertTrue(np.all(received==3))
  self.assertTrue(np.allclose(food,.88))
 def test_temporary_outage_never_creates_physical_food(self):
  alive=np.ones((1,TEAMS,K),dtype=bool)
  outage=np.zeros_like(alive);outage[:,0,0]=True
  food,received=material_food(alive,outage)
  self.assertTrue(np.allclose(food[0,0,1:],
   .2+.55*(2/3)-3*.04))
  self.assertAlmostEqual(float(food[0,0,0]),1.0)
  self.assertAlmostEqual(float(food[0,1,0]),.88)
 def test_matched_environment_independent_of_governor(self):
  a=shocks(999101,3,"HEAVY")
  b=shocks(999101,3,"HEAVY")
  c=shocks(999107,3,"HEAVY")
  self.assertTrue(np.array_equal(a,b))
  self.assertFalse(np.array_equal(a,c))
 def test_local_transfer_conserves_minus_leak(self):
  a=np.asarray([[[1.2,-.2,.6,.1]]],dtype=float)
  alive=np.ones_like(a,dtype=bool)
  z,lost,sent=rescue_local(a,alive)
  self.assertAlmostEqual(float(a.sum())-float(z.sum()),lost,places=8)
  self.assertGreater(sent,0)
  self.assertAlmostEqual(float(z[0,0,1]),0,places=5)
  self.assertGreaterEqual(float(z.min()),-1e-6)
 def test_global_sender_conserves_with_one_step_lag(self):
  stock=np.full((2,TEAMS,K),1.9)
  stock[:,0,:]=.2
  alive=np.ones_like(stock,dtype=bool)
  shock=np.zeros_like(stock,dtype=bool);shock[:,0,0]=True
  gov=GOVERNANCE["FORECAST"]
  b,pending,lost,sent=schedule_global(stock,alive,shock,shock,gov)
  self.assertAlmostEqual(float(stock.sum()-b.sum()-pending.sum()),lost,places=6)
  self.assertGreater(sent,0)
  self.assertTrue(np.all(b>=-1e-7))
 def test_quiet_no_governance_viable_at_exact_food_ceiling(self):
  a=simulate(999101,4,"QUIET","NONE")
  self.assertAlmostEqual(a["survival"],1.)
  self.assertAlmostEqual(a["viable_teams"],1.)
  self.assertAlmostEqual(a["mean_net_food_per_living"],.88,places=9)
  self.assertAlmostEqual(a["admin_per_living"],0)
  self.assertAlmostEqual(a["transfer_loss_per_living"],0)
 def test_organizational_overhead_hurts_quiet_net_output(self):
  a=simulate(999101,4,"QUIET","NONE")
  b=simulate(999101,4,"QUIET","FULL_PROXY")
  self.assertLess(b["mean_net_food_per_living"],a["mean_net_food_per_living"])
  self.assertLessEqual(b["survival"],a["survival"])
if __name__=="__main__":unittest.main()
