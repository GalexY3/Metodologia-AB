import unittest,torch,math
from dataclasses import replace
from train_k import Actor,configure,old

class V14Tests(unittest.TestCase):
    def test_task_features_change_logits(self):
        configure(True)
        c=old.Config(n=60,m=12,k=2,degree=8,batch=3,horizon=3)
        a=Actor(60)
        e=old.World(c,200)
        a.reset()
        torch.manual_seed(11)
        _,_,entropy2=a.act(e,greedy=True)
        with torch.no_grad():
            c.k=3
            a.reset()
            _,_,entropy3=a.act(e,greedy=True)
        self.assertFalse(torch.allclose(entropy2,entropy3))
        configure(False)
        a.reset()
        _,_,entropy_no2=a.act(e,greedy=True)
        c.k=2
        a.reset()
        _,_,entropy_no3=a.act(e,greedy=True)
        self.assertTrue(torch.allclose(entropy_no2,entropy_no3))
    def test_agents_do_not_share_gradients(self):
        configure(True)
        c=old.Config(n=60,m=12,k=2,degree=8,batch=4,horizon=3)
        a=Actor(60)
        e=old.World(c,123)
        _,logp,_=a.act(e)
        loss=-logp[:,0].sum()
        loss.backward()
        for p in a.parameters():
            if p.grad is not None:
                self.assertLess(float(p.grad[1:].abs().max()),1e-9)
    def test_reward_quotas(self):
        c=old.Config(n=60,m=12,k=3,batch=1,horizon=2)
        jobs=torch.tensor([[0]*20+[4]*20+[10]*20])
        r,h=old.food(jobs,c.m,c.k)
        self.assertTrue(torch.allclose(r,torch.ones_like(r)))
        self.assertEqual(int((h>0).sum()),3)
        for k in (2,3,4,5,6,10,12,15):
            n=120
            jobs=torch.arange(n)%k
            r,_=old.food(jobs.unsqueeze(0),40,k)
            self.assertAlmostEqual(float(r.mean()),1.,places=7)
    def test_gradient_training(self):
        configure(True)
        c=old.Config(n=60,m=12,k=3,degree=8,batch=6,horizon=5)
        m=Actor(60)
        opt=torch.optim.Adam(m.parameters(),lr=.009)
        x=old.train_step(m,opt,c,99)
        self.assertTrue(math.isfinite(x['loss']))
        self.assertTrue(0<=x['food']<=1)
if __name__=='__main__':unittest.main(verbosity=2)
