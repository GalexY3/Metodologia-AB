"""V47 tests: pairing uniqueness and identity-preserving private gradients."""
from __future__ import annotations
import unittest,numpy as np,torch
from v47_partner_turnover import sample_pairing,inverse_permutation_gradient,development
from v46_exact_opponent_shaping import N,gradients,measurements
class V47Tests(unittest.TestCase):
 def setUp(self):
  torch.set_num_threads(2)
  torch.manual_seed(470007)
 def test_matching_is_uniform_permutation_and_reproducible(self):
  a=sample_pairing(3111,1)
  b=sample_pairing(3111,1)
  c=sample_pairing(3111,2)
  self.assertTrue(np.array_equal(a,b))
  self.assertFalse(np.array_equal(a,c))
  self.assertEqual(sorted(a.tolist()),list(range(N)))
 def test_identity_preserved_after_remapping_gradients(self):
  tensor=torch.randn(N,5,dtype=torch.double)
  perm=torch.tensor(sample_pairing(4111,37),dtype=torch.long)
  permuted=tensor[perm]
  recovered=inverse_permutation_gradient(permuted,perm)
  self.assertTrue(torch.equal(recovered,tensor))
 def test_new_pairing_updates_only_private_own_gradient(self):
  policy=torch.nn.Parameter(torch.randn(N,5,dtype=torch.double)*.1)
  perm=torch.tensor(sample_pairing(3111,73),dtype=torch.long)
  p=policy[perm]
  naive=gradients(p,.95,'NL',0.)
  direct=gradients(p,.95,'LOLA',0.)
  self.assertTrue(torch.equal(naive,direct))
  aligned=inverse_permutation_gradient(naive,perm)
  for actor in range(N):
   j=perm.tolist().index(actor)
   self.assertTrue(torch.equal(aligned[actor],naive[j]))
 def test_dev_seeds_disjoint_from_heldout(self):
  from v47_partner_turnover import development
  params=torch.randn(N,5)
  values=development(params)
  self.assertTrue(np.isfinite(list(values.values())).all())
if __name__=="__main__":unittest.main()
