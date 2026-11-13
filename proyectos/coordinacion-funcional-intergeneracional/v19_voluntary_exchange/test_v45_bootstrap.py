"""V45 isolation: initial bias only, private actor identity and rewards unchanged."""
import unittest,torch
from v44_private_dyads import PrivateDyadic,simulation
class V45Tests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_initial_bias_is_only_changed_parameter(self):
  torch.manual_seed(45112);a=PrivateDyadic()
  torch.manual_seed(45112);b=PrivateDyadic()
  with torch.no_grad():b.bias.fill_(3.)
  for name,value in a.named_parameters():
   other=dict(b.named_parameters())[name]
   if name=="bias":self.assertTrue(torch.all(other==3))
   else:self.assertTrue(torch.equal(value,other),name)
  self.assertAlmostEqual(float(torch.sigmoid(torch.tensor(3.))),.952574,places=5)
 def test_input_biased_policy_actually_gives_more(self):
  torch.manual_seed(455123);a=PrivateDyadic()
  torch.manual_seed(455123);b=PrivateDyadic()
  with torch.no_grad():b.bias.fill_(3.)
  with torch.no_grad():
   x,*_=simulation(a,980101,batch=128,q=.95,see_partner=True)
   y,*_=simulation(b,980101,batch=128,q=.95,see_partner=True)
  self.assertGreater(y["gifts"],x["gifts"]+.2)
  self.assertGreater(y["food"],x["food"])
if __name__=='__main__':unittest.main()
