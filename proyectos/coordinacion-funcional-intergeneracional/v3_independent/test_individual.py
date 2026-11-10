"""Adversarial invariants for individual, color-equivariant, message-only cooperation."""
import unittest
import torch
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v2_rl"))
from environment import Configuration
from environment_v3 import IndependentSociety
from individual_agents import IndependentActors

torch.set_num_threads(2)

def recolor_observation(obs,perm):
    new=obs.clone()
    new[:,:,:4][:,:,perm]=obs[:,:,:4]
    neigh=obs[:,:,4:24].reshape(*obs.shape[:2],5,4)
    neigh_new=neigh.clone()
    neigh_new[:,:,:,perm]=neigh
    new[:,:,4:24]=neigh_new.flatten(-2)
    return new

def recolor_snapshots(s,perm):
    new=s.clone()
    new[:,:,:,:4][:,:,:,perm]=s[:,:,:,:4]
    neigh=s[:,:,:,4:24].reshape(*s.shape[:3],5,4)
    neigh_new=neigh.clone()
    neigh_new[:,:,:,:,perm]=neigh
    new[:,:,:,4:24]=neigh_new.flatten(-2)
    return new

class IndependentPolicyTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(881)
        self.env=IndependentSociety(Configuration(batch=3,seed=18,randomize_majority=True))
        self.model=IndependentActors(n=36,hidden=12)

    def test_different_weights_for_each_agent(self):
        self.assertTrue(all(p.shape[0]==36 for p in self.model.parameters()))
        self.assertFalse(torch.equal(self.model.choose_W1[0],self.model.choose_W1[1]))

    def test_gradients_cannot_cross_agents(self):
        o=self.env.observe()
        s,slog,sent=self.model.act_send(o,self.env.k)
        incoming,request,payload=self.env.deliveries(o,s)
        c,clog,cent=self.model.act_choose(o,self.env.k,incoming,request,payload)
        # One node log-probability, no reward terms yet.
        (-slog[:,0].sum()-clog[:,0].sum()).backward()
        for name,p in self.model.named_parameters():
            if p.grad is not None:
                self.assertEqual(float(p.grad[1:].abs().sum()),0.,name)

    def test_own_color_change_without_messages(self):
        env=self.env
        env.reset(k=4)
        outgoing=torch.zeros((env.batch,env.n),dtype=torch.long)
        inc,req,snap=env.deliveries(env.observe(),outgoing)
        old=env.colors.clone()
        selected=old.clone()
        selected[0,0]=(old[0,0]+1)%4
        outcome=env.step(outgoing,selected,inc,req)
        self.assertEqual(int(outcome["churn"][0]*env.n),1)
        self.assertEqual(float(outcome["messages"][0]),0.)

    def test_send_and_receive_multiple(self):
        env=IndependentSociety(Configuration(batch=1,seed=7))
        env.reset(k=4)
        target=14
        send=torch.zeros((1,env.n),dtype=torch.long)
        neighbours=list(env.contact_sets[target])
        for i in neighbours:
            slot=int((env.neighbors[i]==target).nonzero()[0])
            send[0,i]=1+slot*4+(i%4)
        # May send even while receiving requests.
        j=neighbours[0]
        self_slot=int((env.neighbors[target]==j).nonzero()[0])
        send[0,target]=1+self_slot*4+1
        inc,req,payload=env.deliveries(env.observe(),send)
        self.assertEqual(int(inc[0,target].sum()),len(neighbours))
        self.assertGreater(int(send[0,target]),0)

    def test_color_choice_exactly_k_without_aliases(self):
        e=self.env
        e.reset(k=2)
        o=e.observe()
        s,_,_=self.model.act_send(o,e.k)
        inc,req,contents=e.deliveries(o,s)
        scores=self.model.choose_logits(o,e.k,inc,req,contents)
        self.assertEqual(tuple(scores.shape),(3,36,4))
        self.assertTrue((scores[:,:,:2]>-1e7).all())
        self.assertTrue((scores[:,:,2:]<-1e7).all())
        c,_,_=self.model.act_choose(o,e.k,inc,req,contents)
        self.assertTrue((c<2).all())

    def test_no_message_snapshot_cannot_leak_into_choice(self):
        e=self.env
        o=e.observe()
        s=torch.zeros((3,e.n),dtype=torch.long)
        inc,req,payload=e.deliveries(o,s)
        a=self.model.choose_logits(o,e.k,inc,req,payload)
        b=self.model.choose_logits(o,e.k,inc,req,torch.randn_like(payload)*99)
        self.assertTrue(torch.allclose(a,b,atol=1e-6))

    def test_exact_color_equivariance_send_and_choose(self):
        e=self.env
        e.reset(k=4)
        o=e.observe()
        send,_,_=self.model.act_send(o,e.k)
        incoming,requested,snap=e.deliveries(o,send)
        perm=torch.tensor([2,0,3,1])
        o2=recolor_observation(o,perm)
        snap2=recolor_snapshots(snap,perm)
        req2=perm[requested]
        logits1=self.model.choose_logits(o,e.k,incoming,requested,snap)
        logits2=self.model.choose_logits(o2,e.k,incoming,req2,snap2)
        self.assertTrue(torch.allclose(logits1,logits2[:,:,perm],atol=2e-6))
        out1=self.model.send_logits(o,e.k)
        out2=self.model.send_logits(o2,e.k)
        self.assertTrue(torch.allclose(out1[:,:,0],out2[:,:,0],atol=2e-6))
        s1=out1[:,:,1:].reshape(3,e.n,5,4)
        s2=out2[:,:,1:].reshape(3,e.n,5,4)
        self.assertTrue(torch.allclose(s1,s2[:,:,:,perm],atol=2e-6))

    def test_world_feedback_one_scalar(self):
        e=self.env
        o=e.observe()
        send=torch.zeros((e.batch,e.n),dtype=torch.long)
        inc,req,payload=e.deliveries(o,send)
        current=e.colors.clone()
        result=e.step(send,current,inc,req)
        self.assertEqual(tuple(result["reward"].shape),(3,))
        self.assertTrue(torch.equal(result["reward"],torch.zeros(3)))

    def test_action_validity(self):
        e=self.env
        e.reset(k=2)
        o=e.observe()
        s,_,_=self.model.act_send(o,e.k)
        inc,req,payload=e.deliveries(o,s)
        c,_,_=self.model.act_choose(o,e.k,inc,req,payload)
        result=e.step(s,c,inc,req)
        self.assertTrue((e.colors<2).all())
        with self.assertRaises(RuntimeError):
            invalid=c.clone();invalid[0,0]=3
            e.step(s,invalid,inc,req)

    def test_params_unchanged_on_evaluation(self):
        init={name:p.detach().clone() for name,p in self.model.named_parameters()}
        e=self.env
        with torch.no_grad():
            for _ in range(3):
                o=e.observe()
                s,_,_=self.model.act_send(o,e.k)
                inc,req,payload=e.deliveries(o,s)
                c,_,_=self.model.act_choose(o,e.k,inc,req,payload)
                e.step(s,c,inc,req)
        self.assertTrue(all(torch.equal(init[name],p) for name,p in self.model.named_parameters()))

if __name__=="__main__":unittest.main()
