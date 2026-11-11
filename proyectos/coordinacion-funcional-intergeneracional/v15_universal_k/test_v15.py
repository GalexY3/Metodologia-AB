import unittest,torch,math
from dataclasses import replace
import v15
from v15 import envlib,OptionActor,NOPS
class V15Tests(unittest.TestCase):
    def test_private_gradients(self):
        c=envlib.Config(n=60,m=24,k=4,degree=8,batch=3,horizon=4)
        w=envlib.World(c,2004);actor=OptionActor(60,12)
        _,lp,_=actor.act(w);(-lp[:,0].sum()).backward()
        for p in actor.parameters():
            if p.grad is not None:
                self.assertLess(float(p.grad[1:].abs().max()),1.e-8)
    def test_fractional_quota_and_large_k(self):
        c=envlib.Config(n=120,m=80,k=80,degree=8,batch=2,horizon=3)
        w=envlib.World(c,3)
        a=OptionActor(120,12)
        z,lp,ent=a.act(w)
        self.assertEqual(tuple(z.shape),(2,120))
        self.assertTrue(bool(((z>=0)&(z<c.m)).all()))
        w.advance(z)
        self.assertEqual(tuple(w.food.shape),(2,120))
    def test_each_operator_proposes_valid_profession(self):
        c=envlib.Config(n=60,m=24,k=6,degree=8,batch=4,horizon=4)
        w=envlib.World(c,11);actor=OptionActor(60,12)
        x,l=actor._features(w);choices=actor._candidates(w,l)
        self.assertEqual(choices.shape[-1],NOPS)
        self.assertTrue(bool(((choices>=0)&(choices<c.m)).all()))
        self.assertTrue(bool((choices[:,:,0]==w.jobs).all()))
        # modal/least role proposals originate from observed neighborhoods
        self.assertTrue(bool((l.gather(2,choices[:,:,1:2])>0).all()))
        self.assertTrue(bool((l.gather(2,choices[:,:,2:3])>0).all()))
        self.assertTrue(bool((l.gather(2,choices[:,:,5:6])==0).all()))
    def test_training_and_disjoint_parameters(self):
        c=envlib.Config(n=60,m=24,k=6,degree=8,batch=5,horizon=5)
        actor=OptionActor(60,12)
        opt=torch.optim.Adam(actor.parameters(),lr=.007)
        before=actor.wx.clone()
        m=envlib.train_step(actor,opt,c,199)
        self.assertTrue(math.isfinite(m['loss']))
        self.assertFalse(torch.allclose(actor.wx,before))
    def test_same_agent_memory_reset(self):
        c=envlib.Config(n=60,m=24,k=2,degree=8,batch=5,horizon=5)
        w=envlib.World(c,21);a=OptionActor(60,12)
        a.act(w);self.assertIsNotNone(a.mem)
        a.reset();self.assertIsNone(a.mem);self.assertIsNone(a.bestjobs)
if __name__=='__main__':unittest.main(verbosity=2)
