"""Invariants for V2 directed negotiation and team reward."""
import unittest
import torch
from environment import VectorSociety,Configuration,lattice,OBS_DIM
from agents import LocalActor,CentralCritic
from train import evaluate

torch.set_num_threads(2)
class V2Tests(unittest.TestCase):
 def test_five_neighbors_and_less_at_edges(self):
  idx,mask,contacts=lattice(6,6)
  self.assertEqual(len(contacts),36)
  self.assertEqual(len(contacts[0]),3)
  self.assertEqual(len(contacts[2*6+2]),5)
  self.assertEqual(len(contacts[1]),4)
  self.assertTrue(all(len(c)<=5 for c in contacts))
  self.assertTrue(all(i in contacts[j] for j,c in enumerate(contacts) for i in c))

 def test_120_agents_topology(self):
  ix,mask,c=lattice(10,12)
  self.assertEqual(len(c),120)
  self.assertEqual(len(c[5*12+6]),5)
  self.assertEqual(len(c[0]),3)

 def test_observation_and_actions(self):
  env=VectorSociety(Configuration(batch=3,seed=123))
  obs=env.observe()
  self.assertEqual(tuple(obs.shape),(3,36,OBS_DIM))
  self.assertEqual(tuple(env.send_mask().shape),(3,36,21))
  self.assertTrue(torch.all(env.send_mask()[:,:,0]))
  for b in range(3):
   for i in range(env.n):
    for s in range(5):
     for c in range(4):
      legal=bool(env.send_mask()[b,i,1+s*4+c])
      self.assertEqual(legal,bool(env.valid[i,s] and c<env.k[b]))

 def test_multiple_incoming_plus_outgoing(self):
  env=VectorSociety(Configuration(batch=1,seed=36))
  env.reset(k=4)
  target=2*6+2
  neighbours=list(env.contact_sets[target])
  send=torch.zeros((1,env.n),dtype=torch.long)
  for j in neighbours:
   slot=(env.neighbors[j]==target).nonzero(as_tuple=True)[0]
   self.assertEqual(len(slot),1)
   send[0,j]=1+int(slot[0])*4+((j%3)+1)
  # Receiver can send even if five neighbors send to it.
  target_neighbor=neighbours[0]
  slot=int((env.neighbors[target]==target_neighbor).nonzero()[0])
  send[0,target]=1+slot*4+2
  obs=env.observe()
  incoming,requested,snapshot=env.deliveries(obs,send)
  self.assertEqual(int(incoming[0,target].sum()),5)
  accept=torch.zeros((1,env.n),dtype=torch.long)
  which=int(incoming[0,target].nonzero()[0])+1
  accept[0,target]=which
  expected=int(requested[0,target,which-1])
  out=env.step(send,accept,incoming,requested)
  self.assertEqual(int(env.colors[0,target]),expected)
  self.assertEqual(int(out["messages"].item()*env.n),len(neighbours)+1)
  self.assertEqual(int(out["requests_received"][0,target]),5)

 def test_invalid_accept_rejected(self):
  env=VectorSociety(Configuration(batch=1,seed=6))
  send=torch.zeros((1,env.n),dtype=torch.long)
  incoming,requested,snap=env.deliveries(env.observe(),send)
  ac=torch.zeros_like(send)
  ac[0,0]=1
  with self.assertRaises(RuntimeError):
   env.step(send,ac,incoming,requested)

 def test_reward_is_exact_progress_difference(self):
  env=VectorSociety(Configuration(batch=1,seed=61))
  env.reset(k=4)
  before=env.tv().clone()
  send=torch.zeros((1,env.n),dtype=torch.long)
  incoming,requested,snap=env.deliveries(env.observe(),send)
  ac=torch.zeros_like(send)
  out=env.step(send,ac,incoming,requested)
  self.assertAlmostEqual(float(out["reward"][0]),0.,places=7)
  self.assertAlmostEqual(float(env.tv()[0]),float(before[0]),places=7)

 def test_reproducibility(self):
  a=VectorSociety(Configuration(batch=3,seed=62))
  b=VectorSociety(Configuration(batch=3,seed=62))
  self.assertTrue(torch.equal(a.colors,b.colors))
  self.assertTrue(torch.equal(a.k,b.k))

 def test_actor_and_critic_shapes(self):
  env=VectorSociety(Configuration(batch=3,seed=63))
  actor=LocalActor(hidden=16)
  obs=env.observe()
  send,lp,ent,z=actor.sample_sender(obs,env.send_mask())
  incoming,req,sender=env.deliveries(obs,send)
  accept,alp,aent=actor.sample_receiver(z,sender,incoming,req)
  self.assertEqual(tuple(send.shape),(3,36))
  self.assertEqual(tuple(accept.shape),(3,36))
  env.step(send,accept,incoming,req)
  critic=CentralCritic(hidden=16)
  self.assertEqual(tuple(critic(env).shape),(3,))

 def test_no_one_sender_can_fix_extreme_initial_imbalance(self):
  n=36
  majority=round(n*.70)
  needed=majority-n//4
  degree=5
  self.assertGreater(needed,degree)

 def test_randomized_majority_color(self):
  selected=[]
  for s in range(20):
   env=VectorSociety(Configuration(batch=1,seed=10000+s,randomize_majority=True))
   env.reset(k=4)
   counts=env.distribution()[0]
   self.assertEqual(int(counts.argmax()),int(counts.argmax()))
   self.assertAlmostEqual(float(counts.max()),25/36,places=6)
   selected.append(int(counts.argmax()))
  self.assertGreaterEqual(len(set(selected)),3)

 def test_counterfactual_reward_single_change(self):
  from train_credit import marginal_credits
  env=VectorSociety(Configuration(batch=1,seed=911))
  env.reset(k=4)
  before=env.tv().clone()
  target=int((env.colors[0]==0).nonzero()[0])
  sender=next(iter(env.contact_sets[target]))
  slot=int((env.neighbors[sender]==target).nonzero()[0])
  send=torch.zeros((1,env.n),dtype=torch.long)
  send[0,sender]=1+slot*4+1
  incoming,requested,snapshot=env.deliveries(env.observe(),send)
  a=torch.zeros_like(send)
  received_slot=int(incoming[0,target].nonzero()[0])+1
  a[0,target]=received_slot
  old=env.colors.clone()
  metrics=env.step(send,a,incoming,requested)
  credit,send_credit=marginal_credits(env,old,a,metrics["tv"])
  self.assertGreater(float(credit[0,target]),0)
  self.assertAlmostEqual(float(credit.sum()),float(metrics["reward"][0]),places=4)
  self.assertAlmostEqual(float(send_credit.sum()),float(metrics["reward"][0]),places=4)

 def test_random_baseline_eval(self):
  a=LocalActor(hidden=16)
  v=evaluate(a,seed=67,batch=3,horizon=10,policy="random",k=3)
  self.assertEqual(v["batch"],3)
  self.assertTrue(0<=v["last_tv_mean"]<=1)
  self.assertTrue(v["max_incoming_requests_observed"]<=5)

if __name__=="__main__":unittest.main()
