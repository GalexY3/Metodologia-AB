"""V7 integrity and smoke tests. CPU, short horizons; no scientific claims."""
import unittest, torch
from experiment import GatedColorGRU, make_model, rollout, train_reinforce, train_es, evaluate
from engine import Settings, Society, COLORS, NC, distance
torch.set_num_threads(2)

class Integrity(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(101)
        self.cfg=Settings(side=6,batch=9,horizon=3,hidden=8,device="cpu")
    def test_endogenous_exact_requires_all_quotas(self):
        s=Society(self.cfg)
        s.k.fill_(4)
        s.colors.fill_(0)
        self.assertAlmostEqual(float(s.calcD()[0]),.75,places=6)
        self.assertFalse(bool(s.exact().any()))
        # N=36, k=4 => nine individuals in each of four arbitrary colors.
        s.colors[:]=torch.tensor([1]*9+[3]*9+[5]*9+[7]*9)
        self.assertEqual(float(s.calcD().max()),0.)
        self.assertTrue(bool(s.exact().all()))
    def test_global_rewards_are_world_level(self):
        p=GatedColorGRU(36,hidden=8)
        r=rollout(p,self.cfg,seed=101,disable_messages=True)
        self.assertEqual(tuple(r["rewards"].shape),(3,9))
        self.assertEqual(tuple(r["logps"][0].shape),(9,36))
    def test_no_communication_does_not_leak(self):
        s=Society(self.cfg)
        p=GatedColorGRU(36,hidden=8)
        p.reset(9,"cpu")
        a=p.decisions(s,disable_messages=True)
        self.assertTrue(bool((a["slot"]==NC).all()))
        self.assertTrue(bool((a["rec"]==0).all()))
        self.assertFalse(bool(a["active"].any()))
    def test_cross_gradients_are_zero(self):
        s=Society(self.cfg)
        p=GatedColorGRU(36,hidden=8)
        p.reset(9,"cpu")
        a=p.decisions(s,disable_messages=True)
        (-a["logp"][:,0].sum()).backward()
        for name,par in p.named_parameters():
            if par.grad is not None:
                self.assertEqual(float(par.grad[1:].abs().sum()),0.,name)
    def test_exchangeable_color_channels(self):
        s=Society(self.cfg)
        p=GatedColorGRU(36,hidden=8)
        perm=torch.tensor([3,5,8,4,7,2,0,6,9,1])
        inv=torch.argsort(perm)
        s2=Society(self.cfg)
        s2.k=s.k.clone()
        s2.colors=perm[s.colors]
        s2.prev_colors=perm[s.prev_colors]
        s2.local=s.local[...,inv]
        s2.ema=s.ema[...,inv]
        s2.prev_recv=s.prev_recv[...,inv]
        s2.D=s.D.clone()
        s2.prev_delta=s.prev_delta.clone()
        s2.prev_churn=s.prev_churn.clone()
        # No prior messages, so prev_sent is -1 in both societies.
        h=torch.zeros(9,36,10,8)
        from experiment import features
        a=p.step(features(s),h)
        b=p.step(features(s2),h)
        self.assertTrue(torch.allclose(b,a[...,inv,:],atol=1e-6))
        self.assertTrue(torch.allclose(p.color_logits(b),p.color_logits(a)[...,inv],atol=1e-6))
    def test_memory_reset_is_exact(self):
        s=Society(self.cfg)
        p=GatedColorGRU(36,hidden=8)
        p.reset(9,"cpu")
        p.decisions(s,disable_messages=True)
        self.assertGreater(float(p.hstate.detach().abs().sum()),0.)
        p.reset(9,"cpu")
        self.assertEqual(float(p.hstate.abs().sum()),0.)
    def test_reinforce_updates_and_finite(self):
        p=GatedColorGRU(36,8)
        opt=torch.optim.AdamW(p.parameters(),lr=.0007)
        old=p.gate_bias.detach().clone()
        x=train_reinforce(p,opt,self.cfg,seed=202,disable_messages=True)
        self.assertTrue(torch.isfinite(torch.tensor(x["loss"])).item())
        self.assertTrue(any(float((w.detach()-z).abs().sum())>0 for w,z in
            [(p.gate_bias,old)]))
    def test_es_is_global_and_does_not_leave_grads(self):
        p=GatedColorGRU(36,8)
        old=p.gate_bias.detach().clone()
        ans=train_es(p,self.cfg,seed=303,directions=2,disable_messages=True)
        self.assertTrue(torch.isfinite(torch.tensor(ans["grad_proxy"])).item())
        self.assertTrue(all(x.grad is None for x in p.parameters()))
        self.assertGreater(float((p.gate_bias.detach()-old).abs().sum()),0.)
    def test_development_fixed_worlds(self):
        p=GatedColorGRU(36,8)
        a=evaluate(p,self.cfg,seed=700101,batch=12,steps=12)
        b=evaluate(p,self.cfg,seed=700101,batch=12,steps=12)
        self.assertEqual(a,b)
        self.assertEqual([r["k"] for r in a],[2,3,4])
    def test_recurrent_and_nonrecurrent_are_distinct(self):
        p=GatedColorGRU(36,8,recurrent=True)
        q=GatedColorGRU(36,8,recurrent=False)
        q.load_state_dict(p.state_dict())
        s=Society(self.cfg)
        p.reset(9,"cpu"); q.reset(9,"cpu")
        p.decisions(s,greedy=True,disable_messages=True)
        q.decisions(s,greedy=True,disable_messages=True)
        self.assertGreater(float(p.hstate.detach().abs().sum()),0.)
        self.assertEqual(float(q.hstate.abs().sum()),0.)

if __name__=="__main__":unittest.main()
