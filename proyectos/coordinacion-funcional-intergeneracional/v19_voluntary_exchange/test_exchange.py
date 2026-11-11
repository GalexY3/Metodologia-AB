"""V19 integrity: private gradients, coalition necessity, arbitrary k, graph, payoff."""
import unittest,torch,math
from exchange import Config,IndependentActors,create_world,advance,make_graph,rollout
class Integrity(unittest.TestCase):
 def setUp(self):torch.set_num_threads(2)
 def config(self,**kwargs):
  return Config(n=60,k=kwargs.pop('k',3),degree=kwargs.pop('degree',8),
    device='cpu',batch=kwargs.pop('batch',3),horizon=kwargs.pop('horizon',3),
    **kwargs)
 def test_no_single_agent_can_obtain_missing_goods(self):
  c=self.config()
  w=create_world(c,101)
  roles=torch.zeros(c.batch,c.n,dtype=torch.long)
  offers=torch.ones(c.batch,c.n)
  r=advance(c,w,roles,offers)
  self.assertTrue(bool((w['coverage']==0).all()))
  self.assertTrue(bool((w['full']==0).all()))
  self.assertTrue(bool((r<.20).all()))
 def test_mutual_exchange_requires_both_opt_in(self):
  c=self.config(k=2)
  w=create_world(c,101)
  roles=torch.arange(60).repeat(c.batch,1)%2
  for i in range(c.batch):
   offers=torch.ones(c.batch,c.n)
   offers[:,0]=0
   w['roles']=roles.clone();w['offers']=torch.zeros_like(offers)
   advance(c,w,roles,offers)
   self.assertEqual(float(w['coverage'][i,0]),0)
  # In the one-way treatment, a recipient can accept a gift without giving.
  w=create_world(self.config(k=2,mutual=False),101)
  advance(self.config(k=2,mutual=False),w,roles,offers)
  self.assertGreater(float(w['coverage'][0,0]),0)
 def test_reward_is_private_and_not_world_mean(self):
  c=self.config(k=2)
  w=create_world(c,101)
  roles=torch.arange(60).repeat(c.batch,1)%2
  offers=torch.ones(c.batch,c.n)
  r=advance(c,w,roles,offers)
  self.assertGreater(float(r.mean()),.20)
  self.assertAlmostEqual(float(r.max()),.88,places=5)
  self.assertEqual(tuple(r.shape),(3,60))
 def test_graph_is_symmetric_and_regular(self):
  for topo in ('ring','rewired'):
   a=make_graph(60,8,topo,123,'cpu').tolist()
   for i,nei in enumerate(a):
    self.assertEqual(len(nei),len(set(nei)))
    self.assertNotIn(i,nei)
    for j in nei:self.assertIn(i,a[j])
 def test_roles_are_permutation_equivariant(self):
  c=self.config(k=4)
  w=create_world(c,101)
  actor=IndependentActors(60,12)
  from exchange import observe
  torch.manual_seed(999)
  logits0=actor.act(c,w,return_logits=True)
  perm=torch.tensor([3,1,0,2])
  copy={x:v.clone() if isinstance(v,torch.Tensor) else v
        for x,v in w.items()}
  copy['roles']=perm[w['roles']]
  torch.manual_seed(999)
  logits1=actor.act(c,copy,return_logits=True)
  self.assertTrue(torch.allclose(logits0,logits1[:,:,perm],atol=1e-6))
 def test_agents_are_truly_parameter_independent(self):
  c=self.config(k=4)
  w=create_world(c,123)
  actor=IndependentActors(60,12)
  _,_,logp,_=actor.act(c,w)
  (-logp[:,0].mean()).backward()
  for name,p in actor.named_parameters():
   if p.grad is not None:
    self.assertLess(float(p.grad[1:].abs().max()),1e-9,name)
 def test_generalization_to_nontrained_k_and_graph(self):
  actor=IndependentActors(60,12)
  for k in (2,3,4,5,6,10,12):
   for top in ('ring','rewired'):
    c=self.config(k=k,degree=12,topology=top)
    z=rollout(c,actor,101)
    self.assertEqual(z['metrics']['worlds'],3)
    self.assertTrue(math.isfinite(z['metrics']['food']))
    self.assertTrue(0<=z['metrics']['offer']<=1)
 def test_zero_cost_is_monotone_in_giving_for_mutual_exchange(self):
  c=self.config(k=2,cost=0.,switch_cost=0.)
  w=create_world(c,99)
  roles=torch.arange(60).repeat(c.batch,1)%2
  offers=torch.ones(c.batch,c.n)
  all_give=advance(c,w,roles,offers).mean().item()
  w=create_world(c,99)
  none_give=advance(c,w,roles,torch.zeros_like(offers)).mean().item()
  self.assertGreater(all_give,none_give)
if __name__=='__main__':unittest.main(verbosity=2)
