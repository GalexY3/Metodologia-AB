"""Deterministic integrity tests: rewards, graphs, observations and individuality."""
import unittest
import torch
import numpy as np
from village import JOBS,FEATURES,SYMBOLS,Config,Village,IndividualRNN,food_of_memberships,measures,network,rollout
torch.set_num_threads(2)

class Tests(unittest.TestCase):
    def setUp(self):
        self.cfg=Config(n=36,batch=8,horizon=4,hidden=8,degree=5)
        torch.manual_seed(801)
    def test_exact_optimum_and_total_unbalance(self):
        for labels in ((0,1,2,3),(2,4,6,9)):
            colors=torch.tensor([[x for job in labels for x in [job]*9]])
            foods,counts=food_of_memberships(colors,36)
            self.assertTrue(bool(torch.allclose(foods,torch.ones_like(foods))))
            self.assertEqual(measures(colors,foods,counts)["D4"],0)
        c=torch.zeros(1,36,dtype=torch.long)
        f,ct=food_of_memberships(c,36)
        self.assertAlmostEqual(float(f[0,0]),.25,places=6)
        self.assertAlmostEqual(measures(c,f,ct)["D4"],.75,places=6)
    def test_under_and_over_size(self):
        c=torch.tensor([[0]+[1]*18+[2]*9+[3]*8])
        f,ct=food_of_memberships(c,36)
        self.assertAlmostEqual(float(f[0,0]),1/9,places=6)
        self.assertAlmostEqual(float(f[0,1]),.5,places=6)
        self.assertAlmostEqual(float(f[0,19]),1,places=6)
    def test_graph_symmetry_degree(self):
        for degree in (2,4,5,8):
            for topology in ("ring","rewired"):
                g=network(36,degree,topology,8)
                self.assertEqual(g.shape,(36,degree))
                for i in range(36):
                    self.assertEqual(len(set(g[i])),degree)
                    self.assertNotIn(i,g[i])
                    for j in g[i]:self.assertIn(i,g[j])
    def test_observations_are_local(self):
        e=Village(self.cfg,seed=313)
        a=e.observations()
        self.assertEqual(a.shape,(8,36,FEATURES))
        self.assertTrue(bool(torch.allclose(a[...,10:20].sum(-1),torch.ones(8,36))))
        self.assertTrue(bool(torch.allclose(a[...,20:25].sum(-1),torch.ones(8,36))))
        # Mutation of remote job outside radius one must not change focal observation,
        # except if it changes own food (choose another job with no impact on focal).
        g=e.graph[0].tolist()
        remote=next(i for i in range(1,36) if i not in g and i!=0 and e.colors[0,i]!=e.colors[0,0])
        before=a[0,0].clone()
        e.colors[0,remote]=(e.colors[0,remote]+1)%JOBS
        e.food,e.counts=food_of_memberships(e.colors,36)
        # Own food can change only if one of moved jobs matches focal job; choose away.
        if (e.colors[0,remote]==e.colors[0,0]):
            e.colors[0,remote]=(e.colors[0,remote]+1)%JOBS
            e.food,e.counts=food_of_memberships(e.colors,36)
        after=e.observations()[0,0]
        self.assertTrue(torch.allclose(before,after))
    def test_blind_removes_social_observations(self):
        from dataclasses import replace
        env=Village(replace(self.cfg,blind=True),seed=313)
        obs=env.observations()
        self.assertEqual(float(obs[...,10:25].abs().sum()),0)
        self.assertGreater(float(obs[...,:10].abs().sum()),0)
        self.assertGreater(float(obs[...,25].abs().sum()),0)
    def test_per_agent_parameter_gradients(self):
        e=Village(self.cfg,seed=471)
        actor=IndividualRNN(36,8)
        actor.reset(8,"cpu")
        _,_,lp,_=actor.choose(e.observations(),e.colors,True,greedy=False)
        (-lp[:,0].sum()).backward()
        for name,p in actor.named_parameters():
            if p.grad is not None:
                self.assertEqual(float(p.grad[1:].abs().max()),0,name)
    def test_rewards_not_global(self):
        c=torch.tensor([[0]+[1]*18+[2]*9+[3]*8])
        f,ct=food_of_memberships(c,36)
        self.assertNotEqual(float(f[0,0]),float(f[0,1]))
        self.assertGreater(float(f[0,19]),float(f[0,1]))
    def test_no_messages_stay_zero(self):
        r=rollout(None,self.cfg,711,baseline="frozen",record=True)
        self.assertEqual(len(r["frames"]),self.cfg.horizon+1)
        self.assertEqual(r["initial"]["D4"],r["final"]["D4"])
        self.assertEqual(r["initial"]["food_mean"],r["final"]["food_mean"])
        e=Village(self.cfg,711)
        for _ in range(4):
            e.advance(e.colors,torch.full_like(e.colors,3))
            self.assertEqual(int(e.messages.sum()),0)
    def test_reproducibility(self):
        a=rollout(None,self.cfg,711,baseline="random",record=True)
        b=rollout(None,self.cfg,711,baseline="random",record=True)
        self.assertEqual(a["frames"],b["frames"])
        self.assertEqual(a["final"],b["final"])

if __name__=="__main__":unittest.main(verbosity=2)
