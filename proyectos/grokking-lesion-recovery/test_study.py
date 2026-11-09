import sys,copy,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import torch
from torch.nn import functional as F
from study import Net,data
torch.set_num_threads(2)

class StudyChecks(unittest.TestCase):
    def test_fixed_split(self):
        x,y,tr,te=data(31,.55,20261109)
        self.assertEqual(len(set(tr.tolist()).intersection(te.tolist())),0)
        self.assertEqual(len(tr)+len(te),961)
        self.assertTrue(torch.equal((x[:,0]+x[:,1])%31,y))
    def test_ablation_permanent_functional_invariance(self):
        torch.manual_seed(15)
        m=Net()
        x,y,tr,te=data(31,.55,20261109)
        with torch.no_grad():
            m.mask[:30]=0
            initial=m(x)
            m.hidden.weight[:30]*=350
            m.hidden.bias[:30]+=10
            m.out.weight[:,:30]*=-150
            altered=m(x)
        self.assertTrue(torch.allclose(initial,altered,atol=1e-5,rtol=1e-5))
    def test_optimizer_state_continuation(self):
        torch.manual_seed(1)
        m=Net();x,y,tr,te=data(31,.55,20261109)
        o=torch.optim.AdamW(m.parameters(),lr=.001,weight_decay=.4)
        def step(model,opt):
            opt.zero_grad(set_to_none=True)
            loss=F.cross_entropy(model(x[tr]),y[tr]);loss.backward();opt.step()
        for i in range(5):step(m,o)
        baseline=copy.deepcopy(m);obase=torch.optim.AdamW(baseline.parameters(),lr=.001,weight_decay=.4);obase.load_state_dict(copy.deepcopy(o.state_dict()))
        resumed=Net();resumed.load_state_dict(copy.deepcopy(m.state_dict()))
        orsm=torch.optim.AdamW(resumed.parameters(),lr=.001,weight_decay=.4);orsm.load_state_dict(copy.deepcopy(o.state_dict()))
        step(baseline,obase);step(resumed,orsm)
        for a,b in zip(baseline.parameters(),resumed.parameters()):
            self.assertTrue(torch.equal(a,b))
    def test_exact_mask_cardinality(self):
        import numpy as np
        idx=np.random.default_rng(11).choice(300,size=round(300*.1),replace=False)
        self.assertEqual(len(set(idx.tolist())),30)

if __name__=="__main__":unittest.main(verbosity=2)
