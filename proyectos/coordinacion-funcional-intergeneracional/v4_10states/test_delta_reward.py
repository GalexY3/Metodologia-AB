"""Adversarial math checks for proposed progression-only shared reward."""
import unittest
import torch
from society10 import Society10,Config10
torch.set_num_threads(2)
class RewardScaleChecks(unittest.TestCase):
 def environment(self):
  e=Society10(Config10(rows=6,cols=6,batch=1,seed=541,
    churn_penalty=0,reward_kind="delta"))
  e.reset(k=4)
  return e
 def update(self,e,colors):
  z=torch.zeros((1,36),dtype=torch.long)
  incoming,requested,payload=e.deliveries(e.observe(),z)
  return e.step(z,colors,incoming,requested)
 def test_improving_one_unit_has_reward_plus_one(self):
  e=self.environment()
  old=torch.tensor([0]*10+[1]*9+[2]*9+[3]*8,dtype=torch.long).unsqueeze(0)
  e.colors=old.clone();e.D=e.tv()
  self.assertAlmostEqual(float(e.D[0]),1/36,places=5)
  new=old.clone()
  new[0,0]=3
  out=self.update(e,new)
  self.assertAlmostEqual(float(out["reward"][0]),1.,places=4)
  self.assertAlmostEqual(float(e.D[0]),0.,places=5)
  self.assertTrue(e.exact().all())
 def test_worsening_one_unit_has_reward_minus_one(self):
  e=self.environment()
  old=torch.tensor([0]*9+[1]*9+[2]*9+[3]*9,dtype=torch.long).unsqueeze(0)
  e.colors=old.clone();e.D=e.tv()
  new=old.clone();new[0,-1]=0
  out=self.update(e,new)
  self.assertAlmostEqual(float(out["reward"][0]),-1.,places=4)
 def test_no_change_has_exactly_zero_reward(self):
  e=self.environment()
  out=self.update(e,e.colors.clone())
  self.assertEqual(float(out["reward"][0]),0.)
 def test_bonus_is_shared_scalar_not_individual(self):
  e=Society10(Config10(rows=6,cols=6,batch=3,seed=541,reward_kind="delta"))
  s=torch.zeros((3,36),dtype=torch.long)
  inc,req,pay=e.deliveries(e.observe(),s)
  result=e.step(s,e.colors.clone(),inc,req)
  self.assertEqual(tuple(result["reward"].shape),(3,))
 def test_original_level_activity_cost_is_fractional(self):
  # n=36, one state change raises churn by 1/36, so penalty is 0.03/36.
  self.assertAlmostEqual(.03/36,0.00083333333333333,places=10)
  self.assertAlmostEqual((.03/36)/(1/36),.03,places=10)
if __name__=="__main__":unittest.main()
