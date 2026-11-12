"""V35 invariants for post-training shocks and genuinely effective role shock."""
from __future__ import annotations
import unittest,numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4
from v35_shock_audit import simulate,apply_shock
class V35Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  self.name='v31_N120_MUTUAL_C04_s3111'
 def test_shock_preperiod_matched_and_occupation_change_effective(self):
  reference=simulate(self.name,970001,'control',worlds=2,device='cpu')
  for shock in ('rewire','roles','newcomers'):
   treated=simulate(self.name,970001,shock,worlds=2,device='cpu')
   before=np.asarray([r['food'] for r in reference['round_trace'][:24]])
   changed=np.asarray([r['food'] for r in treated['round_trace'][:24]])
   self.assertTrue(np.array_equal(before,changed),shock)
   self.assertNotAlmostEqual(reference['food_25_32'],
        treated['food_25_32'],places=5,msg=shock)
 def test_newcomer_own_weights_replace_exactly_quarter(self):
  n=120;c=C(n=n,k=4,degree=6,topology='ring',
   batch=2,horizon=48,cost=.04,device='cpu')
  w=start4(c,970001,'monolith')
  torch.manual_seed(1356)
  donor=PrivateGiftActor(n,8,8.)
  role=PrivateOccupationK(n,4,8)
  spec=dict(hidden=8,init_scale=8.)
  gift2,role2,ids=apply_shock(c,w,donor,role,'newcomers',970001,spec)
  self.assertEqual(int(ids.sum()),30)
  for original,new in ((donor,gift2),(role,role2)):
   changed=False
   for name,v in original.named_parameters():
    z=dict(new.named_parameters())[name]
    self.assertTrue(torch.equal(v[~ids],z[~ids]),name)
    changed=changed or not torch.equal(v[ids],z[ids])
   self.assertTrue(changed,'At least one newly initialized weight must differ')
if __name__=='__main__':unittest.main()
