"""Mechanical dominance of one more gift in a finite terminal round."""
import unittest,torch
from targeted_gifts import C,create,step
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
class TestTerminalGiftDominance(unittest.TestCase):
 def test_v23_terminal_direct_gift_is_private_cost_only(self):
  torch.set_num_threads(2)
  c=C(n=24,k=2,degree=2,topology="ring",batch=3,
      horizon=48,cost=.12,device="cpu")
  w=create(c,1621)
  dest=w["graph"][None,:,0].expand(c.batch,-1)
  zeros=torch.zeros(c.batch,c.n)
  for _ in range(47):step(c,w,dest,zeros)
  yes={k:(v.clone() if torch.is_tensor(v) else v)
     for k,v in w.items()}
  no={k:(v.clone() if torch.is_tensor(v) else v)
     for k,v in w.items()}
  offers=zeros.clone();offers[:,7]=1
  yes_r=step(c,yes,dest,offers)
  no_r=step(c,no,dest,zeros)
  self.assertTrue(torch.allclose(yes_r[:,7]-no_r[:,7],
     torch.full((c.batch,),-.12)))
 def test_v25_terminal_extra_slot_is_private_cost_only(self):
  c=C(n=48,k=4,degree=6,topology="ring",batch=3,
      horizon=48,cost=.04,device="cpu")
  w=start4(c,1621,"balanced")
  dest=w["graph"][None,:,:3].expand(c.batch,-1,-1)
  zero=torch.zeros(c.batch,c.n,3)
  for _ in range(47):step_multi(c,w,dest,zero)
  yes={k:(v.clone() if torch.is_tensor(v) else v)
     for k,v in w.items()}
  no={k:(v.clone() if torch.is_tensor(v) else v)
     for k,v in w.items()}
  one=zero.clone();one[:,7,0]=1
  r_yes,_=step_multi(c,yes,dest,one)
  r_no,_=step_multi(c,no,dest,zero)
  self.assertTrue(torch.allclose(r_yes[:,7]-r_no[:,7],
      torch.full((c.batch,),-.04),atol=1e-5))
if __name__=="__main__":unittest.main()
