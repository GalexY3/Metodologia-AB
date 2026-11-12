"""Mechanical and matched-world invariants for V39 institutional interruption."""
import unittest,torch,numpy as np
from v39_contract_outage import regime,run,ARMS
from v25_holdout import load
class TestV39(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  self.d,self.r,self.spec=load('v30_MUTUAL_C04_s3111','cpu')
 def test_exact_windows(self):
  self.assertEqual(regime('closed8',23),'contract')
  self.assertEqual(regime('closed8',24),'closed')
  self.assertEqual(regime('closed8',31),'closed')
  self.assertEqual(regime('closed8',32),'contract')
  self.assertEqual(regime('unilateral8',31),'unilateral')
  self.assertEqual(regime('unilateral8',32),'contract')
  self.assertEqual(regime('unilateral_permanent',47),'unilateral')
 def test_uninterrupted_first24_bitwise_and_real_closed_market(self):
  arms={arm:run(970001,arm,self.d,self.r,self.spec,worlds=2)
        for arm in ARMS}
  first=arms['control']['trace'][:24]
  for arm in ARMS:
   data=arms[arm]['trace']
   self.assertEqual(first,data[:24],arm)
  closed=arms['closed8']['trace'][24:32]
  self.assertEqual([v['transfers'] for v in closed],[0.]*8)
  self.assertGreater(float(np.mean([v['proposals'] for v in closed])),0.)
  self.assertTrue(all(.18<=v['food']<=.201 for v in closed))
  self.assertGreater(float(np.mean([v['transfers'] for v in arms['unilateral8']['trace'][24:32]])),0.)
  self.assertTrue(all(v['regime']=='contract'
    for v in arms['closed8']['trace'][32:]))
 def test_identical_rng_replay(self):
  x=run(970007,'unilateral8',self.d,self.r,self.spec,worlds=2)
  y=run(970007,'unilateral8',self.d,self.r,self.spec,worlds=2)
  self.assertEqual(x,y)
if __name__=='__main__':unittest.main()
