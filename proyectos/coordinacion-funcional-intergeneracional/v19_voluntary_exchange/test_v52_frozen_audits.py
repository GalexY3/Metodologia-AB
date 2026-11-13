"""V52 frozen intervention and control model invariants."""
import unittest,torch,numpy as np
from v51_endogenous_roles import PrivateRoleActor,N
from v52_frozen_audits import causal_model,SEEDS,CONDITIONS,METRICS
class V52AuditTests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2);torch.manual_seed(521199)
  self.role=PrivateRoleActor().eval().requires_grad_(False)
  self.gift=(torch.randn(N,5)*.05).detach()
 def test_exact_private_cost_and_rng_replay(self):
  for init in ("monolith","random"):
   x=causal_model(self.gift,self.role,SEEDS[0],init,2,"cpu")
   y=causal_model(self.gift,self.role,SEEDS[0],init,2,"cpu")
   self.assertEqual(x,y)
   self.assertAlmostEqual(x["mean_immediate"],-.04,places=5)
   self.assertEqual(len(x["own_effect"]),48)
 def test_environment_seeds_new_and_control_definitions_fixed(self):
  self.assertEqual(len(SEEDS),6)
  self.assertEqual(len(set(SEEDS)),6)
  self.assertFalse(set(SEEDS)&{970001,997101})
  self.assertEqual(len(CONDITIONS),5)
  self.assertIn("terminal_occupations",METRICS)
if __name__=='__main__':unittest.main()
