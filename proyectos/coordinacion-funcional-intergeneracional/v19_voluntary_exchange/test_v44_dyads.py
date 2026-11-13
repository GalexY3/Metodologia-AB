"""V44 private-reward learning, no-contract payoffs and survival checks."""
import unittest,torch,math
from v44_private_dyads import PrivateDyadic,simulation,N,BASE,VALUE,COST
class V44Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2);torch.manual_seed(441125)
  self.m=PrivateDyadic()
 def test_private_parameter_dimensions(self):
  self.assertEqual(self.m.W.shape,(48,5,16))
  self.assertEqual(self.m.v.shape,(48,16))
  self.assertTrue(all(p.shape[0]==N for p in self.m.parameters()))
 def test_cost_and_value_conservation_when_force_all_donations(self):
  a,*_=simulation(self.m,970001,batch=3,q=1,
       see_partner=True,force_t0=1)
  self.assertTrue(BASE-COST<=a["food"]<=BASE+VALUE)
  self.assertGreater(a["mutual"],0)
 def test_no_partner_info_removes_dependency(self):
  b=4;z=torch.zeros(b,N)
  ones=torch.ones_like(z)
  a=self.m.logits(z,z,z,False,False)
  c=self.m.logits(z,ones,z,False,False)
  self.assertTrue(torch.equal(a,c))
 def test_replay_and_life_range(self):
  a,*_=simulation(self.m,970003,batch=12,q=.95,see_partner=True)
  b,*_=simulation(self.m,970003,batch=12,q=.95,see_partner=True)
  self.assertEqual(a,b)
  self.assertTrue(1<=a["lifetime"]<=48)
if __name__=="__main__":unittest.main()
