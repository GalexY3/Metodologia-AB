import unittest
import numpy as np
import torch
from dataclasses import replace
import network_v13 as nw
import mhu_v13 as mhu
from network_v13 import base,build_graph,network_stats,coordinates
class Checks(unittest.TestCase):
    def test_connected_degree_and_network_types(self):
        for t,d in (('ring',4),('torus',4),('torus',8),('torus',12),
                    ('smallworld',8),('random_regular',8),('modular',8),
                    ('hubs',8),('jitter_geo',8),('poisson_geo',8)):
            g=build_graph(120,d,t,971)
            z=network_stats(120,d,t,971)
            self.assertEqual(g.shape[0],120)
            self.assertEqual(z['n'],120)
            self.assertEqual(z['links'],int((g>=0).sum()/2))
            self.assertTrue(np.all((g>=-1)&(g<120)))
            for i in range(120):
                self.assertNotIn(i,g[i].tolist())
            if t in ('ring','torus','smallworld','random_regular','modular'):
                self.assertTrue(np.all((g>=0).sum(1)==d))
            elif t in ('hubs','jitter_geo','poisson_geo'):
                self.assertLess(z['min_degree'],z['max_degree'])
    def test_local_probability_normalized_even_heterogeneous(self):
        for t in ('hubs','poisson_geo','torus'):
            cfg=base.Config(n=120,m=20,k=4,batch=3,degree=8,topology=t)
            nw.TOPO_SEED=991
            e=base.World(cfg,105)
            a=e.local()
            self.assertEqual(tuple(a.shape),(3,120,20))
            self.assertTrue(bool(torch.allclose(a.sum(-1),torch.ones(3,120))))
            # No current state should be encoded as a missing neighbor
            self.assertTrue(bool(torch.all(a>=0)))
    def test_reproducibility(self):
        a=build_graph(120,8,'jitter_geo',100)
        b=build_graph(120,8,'jitter_geo',100)
        self.assertTrue(np.array_equal(a,b))
        self.assertFalse(np.array_equal(a,build_graph(120,8,'poisson_geo',100)))
    def test_no_gradients_between_agents(self):
        nw.TOPO_SEED=100
        c=base.Config(n=60,m=20,k=4,batch=4,degree=8,topology='torus')
        actor=base.IndividualAgent(c.n)
        e=base.World(c,105)
        actor.reset()
        choice,logp,entropy=actor.act(e)
        (-logp[:,0].sum()).backward()
        for p in actor.parameters():
            if p.grad is not None:
                self.assertAlmostEqual(float(p.grad[1:].abs().max()),0,places=9)
    def test_spectrum_global_quota_does_not_imply_mhu(self):
        n=120;xy=coordinates(n)
        # deliberately divide the physical domain into slabs
        marks=np.array([i//30 for i in range(n)],dtype=int)
        self.assertTrue(all((marks==j).sum()==30 for j in range(4)))
        s=mhu.partial_spectrum(marks,xy)
        self.assertGreater(s['mean_ratio'],1.4)
    def test_mhu_shuffled_null_and_constructed_positive(self):
        c=mhu.calibration(n=60,m=10,k=4,seed=1337,reps=100)
        self.assertGreater(c['null']['mean_ratio'],.7)
        self.assertLess(c['null']['mean_ratio'],1.35)
        self.assertLess(c['constructed_positive_control']['mean_ratio'],c['null']['mean_ratio']*.6)
    def test_low_spectrum_is_label_permutation_invariant(self):
        n=120;xy=coordinates(n)
        a=mhu.reference_balanced(n,10,4,xy,88,'low_spectral',900)
        mapping={int(x):int((x+5)%10) for x in np.unique(a)}
        b=np.array([mapping[int(x)] for x in a])
        self.assertAlmostEqual(mhu.partial_spectrum(a,xy)['mean_ratio'],
                               mhu.partial_spectrum(b,xy)['mean_ratio'],places=12)
    def test_payoff_invariant_under_network(self):
        c=base.Config(n=60,m=20,k=5,batch=4,degree=8,topology='hubs')
        nw.TOPO_SEED=101
        a=base.World(c,112)
        nw.TOPO_SEED=222
        b=base.World(replace(c,topology='torus'),112)
        self.assertTrue(torch.equal(a.jobs,b.jobs))
        self.assertTrue(torch.allclose(a.food,b.food))
    def test_window_variance_separates_marked_null_from_constructed_control(self):
        n=120;xy=coordinates(n)
        rng=np.random.default_rng(41)
        a=[mhu.reference_balanced(n,20,4,xy,int(rng.integers(1e9))) for _ in range(30)]
        b=[mhu.reference_balanced(n,20,4,xy,int(rng.integers(1e9)),kind='low_spectral',swaps=1000) for _ in range(8)]
        null=np.mean([mhu.window_variance_ratio(z,xy)['mean_ratio'] for z in a])
        positive=np.mean([mhu.window_variance_ratio(z,xy)['mean_ratio'] for z in b])
        self.assertGreater(null,.75)
        self.assertLess(null,1.25)
        self.assertLess(positive,null)
    def test_training_smoke(self):
        for t in ('torus','poisson_geo'):
            nw.TOPO_SEED=250
            cfg=base.Config(n=60,m=10,k=2,batch=4,horizon=4,degree=8,topology=t)
            actor=base.IndividualAgent(cfg.n)
            opt=torch.optim.Adam(actor.parameters(),lr=.001)
            result=base.train_step(actor,opt,cfg,311)
            self.assertTrue(np.isfinite(result['loss']))
if __name__=='__main__':unittest.main(verbosity=2)
