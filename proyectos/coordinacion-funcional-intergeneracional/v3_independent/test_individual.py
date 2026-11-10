"""Tests for individual non-shared agents plus independent self-change/negotiation."""
import unittest
import torch
from individual_agents import IndependentActors
from environment import Configuration
from environment_v3 import IndependentSociety,ACTION_DIM

torch.set_num_threads(2)

class IndividualityAndAgencyTests(unittest.TestCase):
    def test_separate_parameter_rows(self):
        net=IndependentActors(n=36,hidden=12)
        self.assertTrue(all(p.shape[0]==36 for p in net.parameters()))
        self.assertTrue(any(not torch.equal(p[0],p[1]) for p in net.parameters() if p.ndim>2))

    def test_no_cross_agent_gradient_on_sending(self):
        torch.manual_seed(19)
        net=IndependentActors(n=36,hidden=12)
        env=IndependentSociety(Configuration(batch=3,seed=41,randomize_majority=True))
        s,lp,ent,h=net.act_send(env.observe(),env.send_mask())
        (-lp[:,0].sum()).backward()
        for name,p in net.named_parameters():
            if p.grad is None: continue
            self.assertGreater(float(p.grad[0].abs().sum()),0,name)
            self.assertEqual(float(p.grad[1:].abs().sum()),0,name)

    def test_no_cross_agent_gradient_on_self_choice(self):
        torch.manual_seed(29)
        net=IndependentActors(n=36,hidden=12)
        env=IndependentSociety(Configuration(batch=3,seed=51))
        obs=env.observe()
        s,_,_,h=net.act_send(obs,env.send_mask())
        incoming,req,payload=env.deliveries(obs,s)
        a,lp,_=net.act_accept(h,payload,incoming,req,env.k)
        (-lp[:,0].sum()).backward()
        for name,p in net.named_parameters():
            if p.grad is None: continue
            self.assertEqual(float(p.grad[1:].abs().sum()),0,name)

    def test_self_change_with_zero_messages(self):
        env=IndependentSociety(Configuration(batch=1,seed=1))
        env.reset(k=4)
        outgoing=torch.zeros((1,36),dtype=torch.long)
        inc,req,payload=env.deliveries(env.observe(),outgoing)
        own=torch.zeros_like(outgoing)
        initial=env.colors[0,0].item()
        color=(initial+1)%4
        own[0,0]=1+color
        res=env.step(outgoing,own,inc,req)
        self.assertEqual(env.colors[0,0].item(),color)
        self.assertEqual(float(res["messages"][0]),0)
        self.assertAlmostEqual(float(res["voluntary_changes"][0]),1/36,places=6)
        self.assertEqual(float(res["acceptances"][0]),0)

    def test_accept_request_even_when_sending(self):
        env=IndependentSociety(Configuration(batch=1,seed=3))
        env.reset(k=4)
        center=14
        incoming_from=next(iter(env.contact_sets[center]))
        sender_slot=int((env.neighbors[incoming_from]==center).nonzero()[0])
        own_slot=int((env.neighbors[center]==incoming_from).nonzero()[0])
        s=torch.zeros((1,36),dtype=torch.long)
        color=(int(env.colors[0,center])+1)%4
        s[0,incoming_from]=1+sender_slot*4+color
        s[0,center]=1+own_slot*4+color
        incoming,req,payload=env.deliveries(env.observe(),s)
        incoming_slot=int(incoming[0,center].nonzero()[0])
        a=torch.zeros_like(s)
        a[0,center]=5+incoming_slot # 5..9; index slot0 -> action5
        res=env.step(s,a,incoming,req)
        self.assertEqual(int(env.colors[0,center]),color)
        self.assertAlmostEqual(float(res["acceptances"][0]*36),1.,places=4)
        self.assertAlmostEqual(float(res["messages"][0]*36),2.,places=4)

    def test_request_cannot_be_accepted_if_not_received(self):
        env=IndependentSociety(Configuration(batch=1,seed=4))
        s=torch.zeros((1,36),dtype=torch.long)
        inc,req,payload=env.deliveries(env.observe(),s)
        a=torch.zeros_like(s)
        a[0,0]=5
        with self.assertRaises(RuntimeError):env.step(s,a,inc,req)

    def test_invalid_color_for_k(self):
        env=IndependentSociety(Configuration(batch=1,seed=7))
        env.reset(k=2)
        s=torch.zeros((1,36),dtype=torch.long)
        inc,req,payload=env.deliveries(env.observe(),s)
        a=torch.zeros_like(s)
        a[0,0]=1+3 # Color3 forbidden for k2
        with self.assertRaises(RuntimeError):env.step(s,a,inc,req)

    def test_actor_outputs_legal_actions(self):
        net=IndependentActors(n=36,hidden=12)
        env=IndependentSociety(Configuration(batch=4,seed=123,randomize_majority=True))
        obs=env.observe()
        send,lp,ent,h=net.act_send(obs,env.send_mask())
        incoming,req,payload=env.deliveries(obs,send)
        own,op,oe=net.act_accept(h,payload,incoming,req,env.k)
        self.assertEqual(tuple(send.shape),(4,36))
        self.assertEqual(tuple(own.shape),(4,36))
        self.assertEqual(tuple(env.action_mask(incoming).shape),(4,36,ACTION_DIM))
        res=env.step(send,own,incoming,req)
        self.assertEqual(tuple(res["reward"].shape),(4,))

    def test_weights_frozen_in_evaluation(self):
        net=IndependentActors(n=36,hidden=12)
        previous={k:p.detach().clone() for k,p in net.named_parameters()}
        env=IndependentSociety(Configuration(batch=2,seed=11))
        with torch.no_grad():
            for t in range(4):
                obs=env.observe()
                s,_,_,h=net.act_send(obs,env.send_mask())
                inc,req,payload=env.deliveries(obs,s)
                a,_,_=net.act_accept(h,payload,inc,req,env.k)
                env.step(s,a,inc,req)
        for k,p in net.named_parameters():self.assertTrue(torch.equal(previous[k],p),k)

    def test_collective_reward_scalar_per_society(self):
        env=IndependentSociety(Configuration(batch=2,seed=11))
        s=torch.zeros((2,36),dtype=torch.long)
        inc,req,payload=env.deliveries(env.observe(),s)
        r=env.step(s,s,inc,req)["reward"]
        self.assertEqual(tuple(r.shape),(2,))

if __name__=="__main__": unittest.main()
