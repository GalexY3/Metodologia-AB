"""V48 causal matching and dynamic pair world invariants."""
import unittest,numpy as np
from v48_within_episode_rewire import schedule,uniforms,batched_simulate,paired_one,N,RATES,MEMORIES,load
class V48Tests(unittest.TestCase):
 def test_perfect_bipartite_pairing_and_survival(self):
  for p in (0.,.05,.6,1.):
   pair,alive=schedule(994101,5,p,steps=12)
   self.assertEqual(pair.shape,(12,5,48))
   self.assertTrue(np.array_equal(np.take_along_axis(pair,pair,axis=2),
      np.broadcast_to(np.arange(48),(12,5,48))))
   self.assertTrue(np.all(alive[1:]<=alive[:-1]))
   if p==0:self.assertTrue(np.all(pair==pair[0]))
 def test_exogenous_random_potential_pairings_identical_for_threshold_conditions(self):
  a,_=schedule(994107,4,.05,steps=20)
  b,_=schedule(994107,4,1.,steps=20)
  # At each switch, use the same precomputed candidate regardless of rate.
  for t in range(20):
   for world in range(4):
    if not np.array_equal(a[t,world],a[t-1,world]) if t else False:
     self.assertTrue(np.array_equal(a[t,world],b[t,world]))
 def test_matched_private_t0_cost_and_replay(self):
  x=np.zeros((N,5))
  for rate in (0.,1.):
   for mode in MEMORIES:
    a=paired_one(x,994101,2,rate,mode)
    b=paired_one(x,994101,2,rate,mode)
    self.assertEqual(a,b)
    self.assertAlmostEqual(a['mean_initial'],-.04,places=9)
 def test_food_matches_original_dyadic_value_per_action(self):
  policy=np.zeros((48,5))
  mapping,alive=schedule(994109,2,0.,steps=1)
  u=uniforms(994109,2,steps=1)
  obs=batched_simulate(policy,mapping,alive,u,'carry')
  self.assertTrue(.16<=obs['food']<=.38334)
  self.assertEqual(obs['distinct_partners'],1.)
if __name__=='__main__':unittest.main()
