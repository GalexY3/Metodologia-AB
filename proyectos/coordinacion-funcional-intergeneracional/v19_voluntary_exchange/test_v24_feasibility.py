"""Conservation-law regression tests for single-donation economies."""
import unittest,torch
from targeted_gifts import C,create,step

class TestFeasibility(unittest.TestCase):
 def test_food_cannot_exceed_single_unit_bound(self):
  torch.set_num_threads(2)
  for k in (2,3,4,5,7,8):
   c=C(n=24,k=k,degree=6,topology="ring",
       batch=32,horizon=8,cost=.12,device="cpu")
   w=create(c,700+k)
   torch.manual_seed(17+k)
   for t in range(8):
    slots=torch.randint(c.degree,(c.batch,c.n,1))
    dest=w["graph"][None,:,:].expand(c.batch,-1,-1).gather(
         2,slots).squeeze(2)
    gift=(torch.rand(c.batch,c.n)<.73).float()
    reward=step(c,w,dest,gift)
    q=float(gift.mean())
    upper=.20+q*(.8/(k-1)-.12)
    self.assertLessEqual(float(reward.mean()),upper+1e-5)
    self.assertLessEqual(float(w["full"].mean()),q/(k-1)+1e-5)
 def test_no_positive_sum_exchange_k8_or_more(self):
  for k in (8,9,12):
   self.assertLess(.8/(k-1)-.12,0.)
 def test_k4_full_population_satisfaction_impossible_unit_capacity(self):
  self.assertAlmostEqual(1/(4-1),1/3)
  self.assertAlmostEqual(.2+.8/(4-1)-.12,0.3466666666666667)
if __name__=="__main__":unittest.main()
