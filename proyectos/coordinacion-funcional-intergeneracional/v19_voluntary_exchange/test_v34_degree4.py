"""V34 topological feasibility and no central role allocation invariants."""
import unittest,torch
from targeted_gifts import C
from v24_k4_joint import start4,adjacent_potential
from v34_frozen_audits import oracle
from v30_consensual import contract_step
class TestScarcity(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  self.c=C(n=48,k=4,degree=4,topology='ring',
           batch=3,horizon=8,cost=.04,device='cpu')
 def test_constructive_three_reciprocal_beneficial_partners(self):
  data=oracle(self.c)
  self.assertAlmostEqual(data['food'],.88,places=5)
  self.assertAlmostEqual(data['full'],1.,places=6)
  self.assertAlmostEqual(data['cover'],1.,places=6)
 def test_initially_monolithic_without_roles_has_no_complement(self):
  w=start4(self.c,1717,'monolith')
  self.assertAlmostEqual(adjacent_potential(self.c,w),0.)
 def test_periodic_occupations_cover_three_missing_types(self):
  w=start4(self.c,1717,'balanced')
  self.assertAlmostEqual(adjacent_potential(self.c,w),1.)
if __name__=='__main__':unittest.main()
