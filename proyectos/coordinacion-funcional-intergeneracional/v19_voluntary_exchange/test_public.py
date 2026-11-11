"""Test the social dilemma: a donor can benefit neighbors while personally losing."""
import unittest,torch
from exchange import Config,create_world
from public_goods import advance,marginal_spillover
class PublicGoods(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def test_no_goods_without_donors(self):
  c=Config(n=60,k=2,degree=2,topology='ring',batch=4,horizon=3,device='cpu')
  w=create_world(c,123)
  roles=torch.arange(60).repeat(4,1)%2
  advance(c,w,roles,torch.zeros(4,60))
  self.assertTrue(bool((w['coverage']==0).all()))
  self.assertTrue(bool((w['full']==0).all()))
 def test_deliberate_costly_donation_spillover(self):
  c=Config(n=60,k=2,degree=2,topology='ring',batch=2,horizon=3,device='cpu')
  w=create_world(c,123)
  roles=torch.zeros(2,60,dtype=torch.long);roles[:,0]=1;roles[:,1]=1
  offers=torch.ones(2,60)
  effect=marginal_spillover(c,w,roles,offers,[0])[0]
  self.assertLess(effect['donor_private'],0.0)
  self.assertGreater(effect['neighbor_external'],0.0)
  self.assertGreater(effect['neighbor_external'],abs(effect['donor_private']))
 def test_free_rider_can_consume_without_donating(self):
  c=Config(n=60,k=2,degree=2,topology='ring',batch=2,horizon=2,device='cpu')
  w=create_world(c,123)
  roles=torch.arange(60).repeat(2,1)%2
  roles[:,59]=0  # node 0 sees both distinct goods from its two neighbors
  offers=torch.ones(2,60);offers[:,0]=0
  advance(c,w,roles,offers)
  self.assertEqual(float(w['full'][0,0]),1.)
  self.assertEqual(float(w['offers'][0,0]),0.)
if __name__=='__main__':unittest.main(verbosity=2)
