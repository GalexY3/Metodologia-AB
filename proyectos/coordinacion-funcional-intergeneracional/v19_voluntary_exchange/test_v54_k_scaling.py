"""V54 variable-k private learning and physical invariants."""
import unittest
import torch,numpy as np
from v54_k_scaling import (N,KS,topology,PrivateOccupationK,donor_source,
 config,episode,physical_return)
class V54Tests(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2);torch.manual_seed(54001)
 def test_k_networks_exact_and_reciprocal(self):
  for k in KS:
   neigh,rev=topology(k)
   self.assertEqual(tuple(neigh.shape),(N,k-1))
   for i in range(N):
    for slot,j in enumerate(neigh[i].tolist()):
     self.assertEqual(int(neigh[j,rev[i,slot]]),i)
     self.assertEqual(i//k,j//k)
 def test_private_actors_all_k_and_normalized_logits(self):
  for k in KS:
   m=PrivateOccupationK(k)
   self.assertEqual(tuple(m.w1.shape),(N,2*k+3,24))
   self.assertTrue(all(p.shape[0]==N for p in m.parameters()))
   c=config(k,2,"cpu")
   x=torch.randint(k,(2,N))
   z=m.logits(x,c["neighbors"],torch.zeros(2,N),torch.zeros(2,N),0)
   self.assertEqual(tuple(z.shape),(2,N,k))
   self.assertTrue(torch.allclose(z.softmax(-1).sum(-1),torch.ones(2,N)))
 def test_oracle_cooperation_has_equal_physical_ceiling_for_all_k(self):
  donor=torch.full((N,5),25.)
  for k in KS:
   actor=PrivateOccupationK(k)
   x,*_=episode(config(k,2,"cpu"),donor,actor,540101,
    init="monolith",baseline="oracle_roles",collect_grad=False)
   self.assertAlmostEqual(x["terminal_food"],.88,places=5)
   self.assertAlmostEqual(x["terminal_balance"],1.,places=6)
   self.assertAlmostEqual(x["terminal_full"],1.,places=6)
 def test_fixed3_conserves_gift_capacity_and_full_coverage_bound(self):
  donor=torch.full((N,5),25.)
  for k in (5,6,8,10,12):
   actor=PrivateOccupationK(k)
   x,*_=episode(config(k,2,"cpu"),donor,actor,540104,
    init="monolith",baseline="oracle_roles",technology="FIXED3",collect_grad=False)
   self.assertLessEqual(x["full"],3/(k-1)+1e-7)
   self.assertLessEqual(x["gifts_per_person"],3+1e-7)
 def test_cost_normalization_and_k4_original_material_parity(self):
  for k in (2,4,12):
   c=config(k,1,"cpu")
   roles=(torch.arange(N)%k)[None,:]
   others=roles[:,c["neighbors"]]
   a=torch.ones(1,N,k-1,dtype=torch.long)
   x=physical_return(roles,others,a,a,k,"ELASTIC")[0]
   y=physical_return(roles,others,a,a,k,"PER_LINK04")[0]
   self.assertTrue(torch.allclose(x,torch.full_like(x,.88),atol=1e-6))
   self.assertTrue(torch.allclose(y,torch.full_like(y,1.-.04*(k-1)),atol=1e-6))
 def test_donor_source_fixed_per_identity_across_k(self):
  for method in ("LOLA20","NL"):
   a,ids=donor_source(method,3111,"cpu")
   b,ids2=donor_source(method,3111,"cpu")
   self.assertEqual(tuple(a.shape),(N,5))
   self.assertTrue(torch.equal(a,b))
   self.assertEqual(ids,ids2)
 def test_monolith_fixed_no_complementary_goods(self):
  for k in (2,4,12):
   m=PrivateOccupationK(k)
   x,*_=episode(config(k,2,"cpu"),torch.full((N,5),25.),m,540111,
     init="monolith",baseline="fixed",collect_grad=False)
   self.assertEqual(x["terminal_balance"],0.)
   self.assertEqual(x["terminal_full"],0.)
   self.assertEqual(x["coverage"],0.)
   self.assertLess(x["food"],.21)
 def test_gradients_private_and_finite(self):
  k=5;c=config(k,3,"cpu");actor=PrivateOccupationK(k)
  donor,_=donor_source("LOLA20",3111,"cpu")
  x,rewards,lp,en,times=episode(c,donor,actor,540111)
  loss=-(torch.stack(lp)*rewards.detach()[times]).mean()
  loss.backward()
  self.assertEqual(len(times),6)
  self.assertTrue(all(p.grad is not None and torch.isfinite(p.grad).all()
   for p in actor.parameters()))
if __name__=="__main__":unittest.main()
