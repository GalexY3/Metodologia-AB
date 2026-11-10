"""Checks for V10 41/57/73-parameter independent neural agents."""
import os,unittest,torch
import village
from micro_agent import MicroAgent
torch.set_num_threads(2)
class Tests(unittest.TestCase):
    def test_param_counts(self):
        for name,count in (("basic",41),("food",57),("public",73)):
            os.environ["VILLAGE_MICRO_MODE"]=name
            a=MicroAgent(36,12)
            self.assertEqual(sum(x.numel() for x in a.parameters()),36*count)
    def test_independent_parameters(self):
        os.environ["VILLAGE_MICRO_MODE"]="food"
        torch.manual_seed(1)
        a=MicroAgent(36,12)
        self.assertFalse(bool(torch.allclose(a.W[0],a.W[1])))
        e=village.Village(village.Config(n=36,batch=8,k=4),100)
        a.reset(8,"cpu")
        _,_,lp,_=a.choose(e.observations(),e.colors,False)
        (-lp[:,0].sum()).backward()
        for p in a.parameters():
            self.assertEqual(float(p.grad[1:].abs().max()),0)
    def test_same_weights_treat_all_colors_equally(self):
        os.environ["VILLAGE_MICRO_MODE"]="basic"
        a=MicroAgent(36,12)
        x=torch.rand(4,36,10,3)
        h=torch.tanh(torch.einsum("bncd,ndh->bnch",x,a.W)+a.b[None,:,None,:])
        out=torch.einsum("bnch,nh->bnc",h,a.V)+a.bias[None,:,None]
        perm=torch.tensor([5,4,3,2,1,0,6,9,8,7])
        q=x[:,:,perm]
        h2=torch.tanh(torch.einsum("bncd,ndh->bnch",q,a.W)+a.b[None,:,None,:])
        out2=torch.einsum("bnch,nh->bnc",h2,a.V)+a.bias[None,:,None]
        self.assertTrue(bool(torch.allclose(out2,out[:,:,perm])))
    def test_public_food_is_realized_not_a_counterfactual(self):
        os.environ["VILLAGE_MICRO_MODE"]="public"
        cfg=village.Config(n=36,k=2,batch=8)
        a=MicroAgent(36,12)
        e=village.Village(cfg,123)
        obs=e.observations()
        gf=obs[...,25].mean(dim=1)
        self.assertTrue(torch.allclose(gf,e.food.mean(1)))
        self.assertEqual(obs.shape[-1],28)
        a.reset(8,"cpu")
        new,_,lp,_=a.choose(obs,e.colors,False)
        self.assertEqual(new.shape,(8,36))
    def test_reproducibility_no_carryover(self):
        os.environ["VILLAGE_MICRO_MODE"]="food"
        a=MicroAgent(36,12)
        e=village.Village(village.Config(n=36,k=4,batch=8),123)
        a.reset(8,"cpu")
        torch.manual_seed(12);x=a.choose(e.observations(),e.colors,False)
        a.reset(8,"cpu")
        torch.manual_seed(12);y=a.choose(e.observations(),e.colors,False)
        self.assertTrue(torch.equal(x[0],y[0]))
if __name__=="__main__":unittest.main(verbosity=2)
