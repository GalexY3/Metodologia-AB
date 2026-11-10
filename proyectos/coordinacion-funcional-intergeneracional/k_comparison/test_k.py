"""Integrity and experimental equivalence checks for k=2 vs k=4."""
import unittest, importlib.util
from pathlib import Path
import torch
from village import Config,Village,IndividualRNN,food_of_memberships,measures
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("v9_original",ROOT.parent/"v9_village"/"village.py")
legacy=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=legacy
spec.loader.exec_module(legacy)
torch.set_num_threads(2)

class Tests(unittest.TestCase):
    def test_optima_for_any_professions(self):
        for k in (2,4):
            for n in (36,324):
                q=n//k
                for labels in ((0,1,2,3)[:k],(8,4,7,2)[:k]):
                    c=torch.tensor([[j for label in labels for j in [label]*q]])
                    f,counts=food_of_memberships(c,n,k)
                    self.assertTrue(bool(torch.allclose(f,torch.ones_like(f))))
                    self.assertAlmostEqual(measures(c,f,counts,k)["Dk"],0,places=7)
    def test_hunger_means_two_farther_from_random_start(self):
        c=torch.tensor([[i%10 for i in range(324)]])
        f2,_=food_of_memberships(c,324,2)
        f4,_=food_of_memberships(c,324,4)
        self.assertLess(float(f2.mean()),float(f4.mean()))
    def test_monopoly_is_a_bad_local_trap(self):
        for k in (2,4):
            n=324;c=torch.zeros(1,n,dtype=torch.long)
            f,_=food_of_memberships(c,n,k)
            self.assertAlmostEqual(float(f[0,0]),1/k,places=6)
            next=c.clone();next[0,0]=1
            fnext,_=food_of_memberships(next,n,k)
            self.assertLess(float(fnext[0,0]),float(f[0,0]))
    def test_rewards_unchanged_at_k4(self):
        c=torch.randint(10,(7,36))
        a,ac=food_of_memberships(c,36,4)
        b,bc=legacy.food_of_memberships(c,36)
        self.assertTrue(torch.equal(a,b))
        self.assertTrue(torch.equal(ac,bc))
    def test_actor_inputs_do_not_include_k(self):
        cfg2=Config(n=36,k=2,batch=8)
        cfg4=Config(n=36,k=4,batch=8)
        a=Village(cfg2,100);b=Village(cfg4,100)
        # Observations differ only because own food and delta differ; actor
        # does not see k, q, or global counts.
        x=a.observations();y=b.observations()
        self.assertTrue(torch.allclose(x[...,:25],y[...,:25]))
        self.assertGreater(float((x[...,25]-y[...,25]).abs().sum()),0)
    def test_gradient_separation(self):
        cfg=Config(n=36,k=2,batch=8,hidden=8)
        a=Village(cfg,100)
        net=IndividualRNN(36,8)
        net.reset(8,"cpu")
        _,_,lp,_=net.choose(a.observations(),a.colors,False)
        (-lp[:,0].sum()).backward()
        for param in net.parameters():
            if param.grad is not None:
                self.assertEqual(float(param.grad[1:].abs().sum()),0)
    def test_deterministic_environment(self):
        for k in (2,4):
            a=Village(Config(k=k),123)
            b=Village(Config(k=k),123)
            self.assertTrue(torch.equal(a.colors,b.colors))
            self.assertTrue(torch.equal(a.food,b.food))

if __name__=="__main__":unittest.main(verbosity=2)
