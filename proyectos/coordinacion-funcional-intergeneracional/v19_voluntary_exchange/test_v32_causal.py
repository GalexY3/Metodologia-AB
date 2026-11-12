"""Frozen mode-intervention and reproducibility checks (V32)."""
import unittest,torch,numpy as np
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK
from v32_institution_choice import PrivateInstitutionActor
from v32_frozen_audits import forced
class TestInstitutionalChoiceCausal(unittest.TestCase):
 def setUp(self):
  torch.manual_seed(19912);torch.set_num_threads(2)
  self.c=C(n=48,k=4,degree=6,topology='ring',
    batch=2,horizon=8,cost=.04,device='cpu')
  self.gift=PrivateGiftActor(48,8,8.)
  self.role=PrivateOccupationK(48,4,8)
  self.mode=PrivateInstitutionActor(48,4,8,initial_bias=-2.)
 def test_both_arms_frozen_replay_exactly(self):
  for value in (0,1):
   a=forced(self.c,self.gift,self.role,self.mode,seed=181,
     init='monolith',social=True,value=value)
   b=forced(self.c,self.gift,self.role,self.mode,seed=181,
     init='monolith',social=True,value=value)
   for key in ('total','initial','future'):
    self.assertTrue(np.array_equal(a[key],b[key]))
 def test_counterfactual_effect_has_decomposition(self):
  a=forced(self.c,self.gift,self.role,self.mode,seed=181,
     init='random',social=True,value=1)
  b=forced(self.c,self.gift,self.role,self.mode,seed=181,
     init='random',social=True,value=0)
  for key in a:
   self.assertEqual(a[key].shape,(2,48))
  self.assertTrue(np.allclose(a['total']-b['total'],
    (a['initial']-b['initial'])+(a['future']-b['future']),atol=1e-5))
if __name__=='__main__':unittest.main()
