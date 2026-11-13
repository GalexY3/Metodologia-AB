"""V54 preregistered frozen controls and accounting invariants."""
import unittest,torch,numpy as np
from v54_k_scaling import N,KS,CONTROLS,TECHS,config,episode,PrivateOccupationK
from v54_frozen_audits import SEEDS,INIT,KEYS
class V54AuditTests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_heldout_seeds_are_six_unique_and_new(self):
  self.assertEqual(len(set(SEEDS)),6)
  self.assertFalse(set(SEEDS)&{997101,998101,999101})
  self.assertEqual(set(INIT),{"monolith","random"})
  self.assertEqual(len(TECHS),3);self.assertEqual(len(CONTROLS),6)
 def test_role_controls_do_not_create_food_when_no_gift(self):
  for k in (2,4,12):
   ctx=config(k,2,"cpu")
   role=PrivateOccupationK(k)
   donor=torch.full((N,5),-35.)
   for baseline in ("fixed","oracle_roles","random_0.35"):
    m,*_=episode(ctx,donor,role,SEEDS[0],init="monolith",
      baseline=baseline,collect_grad=False)
    self.assertLess(m["food"],.201)
    self.assertEqual(m["full"],0.)
    if baseline=="oracle_roles":self.assertAlmostEqual(m["terminal_balance"],1.)
 def test_oracle_private_gifts_and_cost_tech_sensitivity(self):
  k=12;ctx=config(k,2,"cpu");role=PrivateOccupationK(k)
  donor=torch.full((N,5),35.)
  data={}
  for tech in TECHS:
   m,*_=episode(ctx,donor,role,SEEDS[0],init="monolith",
       baseline="oracle_roles",technology=tech,collect_grad=False)
   data[tech]=m
  self.assertGreater(data["ELASTIC"]["food"],data["PER_LINK04"]["food"])
  self.assertGreater(data["ELASTIC"]["full"],data["FIXED3"]["full"])
  self.assertAlmostEqual(data["ELASTIC"]["terminal_food"],.88,places=5)
if __name__=="__main__":unittest.main()
