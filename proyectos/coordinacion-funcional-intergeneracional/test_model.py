"""P0 invariants; run with py -3.14 -m unittest -v test_model.py."""
import unittest
import numpy as np
from model import Society,make_ring,minimum_tv_discrete,train_individual_policies

class ModelInvariants(unittest.TestCase):
    def test_ring_degree_no_self(self):
        edges,neigh=make_ring(120)
        self.assertEqual(len(edges),240)
        self.assertTrue(all(len(x)==4 and i not in x for i,x in enumerate(neigh)))

    def test_one_partner_per_tick(self):
        soc=Society(4,23)
        pairs=soc.matching()
        flat=[a for pair in pairs for a in pair]
        self.assertEqual(len(flat),len(set(flat)))
        self.assertLessEqual(len(flat),120)
        self.assertGreater(len(flat),0)
        soc.tick("minority")
        self.assertLessEqual(soc.history[-1]["matched_agents"],120)

    def test_color_domain_population_constant(self):
        for k in (1,2,3,4,5,8):
            soc=Society(k,12345+k)
            for _ in range(15):
                soc.tick("random")
                self.assertEqual(len(soc.colors),120)
                self.assertTrue(np.all(soc.colors>=0))
                self.assertTrue(np.all(soc.colors<k))

    def test_k1_trivial(self):
        soc=Society(1,789)
        summary=soc.run(20,"learned",learning=True)
        self.assertEqual(summary["final_tv"],0)
        self.assertEqual(summary["tail_churn_mean"],0)
        self.assertTrue(np.all(soc.colors==0))

    def test_discrete_tv(self):
        self.assertEqual(minimum_tv_discrete(120,4),0)
        self.assertEqual(minimum_tv_discrete(120,8),0)
        self.assertGreater(minimum_tv_discrete(120,7),0)
        self.assertAlmostEqual(minimum_tv_discrete(120,7), .5*sum(
            abs(v/120-1/7) for v in [18]+[17]*6))

    def test_reproducible_same_seed(self):
        a=Society(4,987)
        b=Society(4,987)
        aa=a.run(40,"learned",learning=True)
        bb=b.run(40,"learned",learning=True)
        self.assertEqual(a.history,b.history)
        self.assertEqual(aa,bb)
        np.testing.assert_allclose(a.theta,b.theta,rtol=0,atol=0)

    def test_frozen_policy_not_learned(self):
        soc=Society(5,23)
        previous=soc.theta.copy()
        soc.run(80,"learned",learning=False)
        np.testing.assert_array_equal(previous,soc.theta)
        train=Society(4,23)
        initial=train.theta.copy()
        train.run(80,"learned",learning=True)
        self.assertGreater(float(np.max(np.abs(train.theta-initial))),1e-6)

    def test_training_unknown_k_never_used(self):
        weights,history=train_individual_policies(45,episodes_per_k=1,ticks=20)
        self.assertEqual(set(z["k"] for z in history),{2,3,4})
        self.assertEqual(weights.shape,(120,3))
        novel=Society(8,46,theta=weights)
        novel.run(15,"learned",learning=False)
        self.assertTrue(np.all((novel.colors>=0)&(novel.colors<8)))

    def test_decision_uses_no_global_counts(self):
        soc=Society(4,11)
        original=soc.population_counts
        def prohibited():
            raise AssertionError("Agent attempted to use population totals")
        soc.population_counts=prohibited
        for i in range(10):
            _=soc._choose(i,0,"learned",learning=True)
            _=soc._choose(i,0,"minority",learning=False)
        soc.population_counts=original

    def test_biased_initialization(self):
        soc=Society(8,11)
        counts=soc.population_counts()
        self.assertEqual(int(counts.sum()),120)
        self.assertEqual(int(counts[0]),84)
        self.assertGreater(soc.global_tv(),.30)

if __name__=="__main__":unittest.main()
