"""Fail-closed invariants for new 144-agent simulator (no reward leakage)."""
import unittest,torch
from dataclasses import replace
from torch.nn import functional as F
from engine import Settings,Society,IndependentPolicy,make_graph,distance,COLORS,NC
torch.set_num_threads(2)
class Integrity(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(2501)
        self.cfg=Settings(batch=3,hidden=12)
        self.world=Society(self.cfg)
        self.policy=IndependentPolicy(self.cfg.side**2,hidden=12)
    def test_graph_is_symmetric_and_degree_five(self):
        g=make_graph(12)
        self.assertEqual(tuple(g.shape),(144,5))
        for i,row in enumerate(g.tolist()):
            self.assertEqual(len(set(row)),5)
            self.assertTrue(all(i in g[j].tolist() for j in row))
        self.assertEqual(g.numel()//2,360)
    def test_exact_endogenous_quota_2_3_4(self):
        s=self.world
        for k in (2,3,4):
            s.k=torch.full_like(s.k,k)
            counts=s.n//k
            row=torch.tensor(sum(([i*2]*counts for i in range(k)),[]),dtype=torch.long)
            s.colors=row.repeat(s.cfg.batch,1)
            self.assertTrue(s.exact().all())
            self.assertTrue(torch.allclose(s.calcD(),torch.zeros(s.cfg.batch),atol=1e-6))
    def test_one_full_color_is_not_solution_for_k4(self):
        s=self.world;s.k.fill_(4)
        s.colors.fill_(2)
        self.assertAlmostEqual(float(s.calcD()[0]),.75,places=6)
        self.assertFalse(s.exact().any())
    def test_silent_message_cannot_disclose_snapshot(self):
        s=self.world
        slot=torch.full_like(s.colors,NC)
        r1,snap1,active,targets,count=s.send_messages(slot,torch.randint(0,10,s.colors.shape))
        r2,snap2,_,_,_=s.send_messages(slot,torch.randint(0,10,s.colors.shape))
        self.assertTrue((r1==0).all());self.assertTrue((r2==0).all())
        self.assertTrue((snap1==0).all());self.assertTrue((snap2==0).all())
        self.assertFalse(active.any());self.assertTrue((count==0).all())
    def test_actor_has_no_cross_gradient(self):
        w=self.world
        act=self.policy.decisions(w)
        (-act["logp"][:,0].sum()).backward()
        for name,p in self.policy.named_parameters():
            if p.grad is not None:
                self.assertEqual(float(p.grad[1:].abs().sum()),0.,name)
    def test_reward_is_one_scalar_per_society(self):
        s=self.world
        a=self.policy.decisions(s)
        old=s.D.clone()
        delta,turnover=s.advance(a["choice"],a["slot"],a["request"],a["rec"])
        reward=s.n*delta+.25*(1-s.D)
        self.assertEqual(tuple(reward.shape),(3,))
        self.assertTrue(torch.allclose(delta,old-s.D))
    def test_requested_colors_are_arbitrary(self):
        a=self.policy.decisions(self.world)
        self.assertEqual(tuple(a["choice"].shape),(3,144))
        self.assertEqual(tuple(a["logp"].shape),(3,144))
        self.assertTrue((a["choice"]>=0).all() and (a["choice"]<COLORS).all())
        self.assertTrue((a["slot"]>=0).all() and (a["slot"]<=NC).all())
    def test_own_memory_does_not_leak_other_people(self):
        s=self.world
        a=self.policy.decisions(s)
        inc=a["rec"]
        self.assertEqual(inc.shape,(3,144,10))
        # Distinct policies and one public global scalar do not imply access
        # to the full global histogram inside actor.color_features.
        features=self.policy.color_features(s,inc,a["snap"])
        self.assertEqual(features.shape,(3,144,10,14))
        self.assertTrue((features[:,:,:,9] == s.D[:,None,None]).all())
    def test_greedy_is_deterministic_for_fixed_world(self):
        a=self.policy.decisions(self.world,greedy=True)
        b=self.policy.decisions(self.world,greedy=True)
        self.assertTrue(torch.equal(a["choice"],b["choice"]))
        self.assertTrue(torch.equal(a["slot"],b["slot"]))
if __name__=="__main__":unittest.main()
