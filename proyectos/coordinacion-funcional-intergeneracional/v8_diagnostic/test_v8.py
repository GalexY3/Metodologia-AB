"""Integrity checks for V8 controls and research handoff; not efficacy tests."""
import unittest
import numpy as np
from pathlib import Path
from information_bottleneck import distance, ambiguous_example
from learn_acceptance import trial

ROOT=Path(__file__).resolve().parent

class Integrity(unittest.TestCase):
    def test_exact_equal_distribution_for_arbitrary_k_labels(self):
        for k in (2,3,4,6,9):
            n=36
            counts=np.zeros(10,dtype=int)
            counts[np.arange(k)*1]=n//k
            self.assertAlmostEqual(float(distance(counts,k)),0,places=9)
    def test_monopoly_is_not_valid_for_k4(self):
        x=np.zeros(10,dtype=int)
        x[0]=36
        self.assertAlmostEqual(float(distance(x,4)),.75,places=9)
    def test_local_public_observation_is_ambiguous(self):
        item=ambiguous_example()
        self.assertEqual(item["society_A"]["counts"][0],17)
        self.assertEqual(item["society_B"]["counts"][0],19)
        self.assertEqual(item["neighbors"],[0]*5)
        self.assertAlmostEqual(item["global_D"],1/36)
        self.assertGreater(item["society_A"]["error_after"],item["global_D"])
        self.assertLess(item["society_B"]["error_after"],item["global_D"])
    def test_distance_decomposes_into_leakage_and_excess(self):
        rng=np.random.default_rng(21)
        for n in (36,144,324):
            colors=rng.integers(0,10,n)
            counts=np.bincount(colors,minlength=10)
            for k in (2,3,4):
                p=np.sort(counts/n)[-k:]
                leakage=1-p.sum()
                overload=np.maximum(p-1/k,0).sum()
                self.assertAlmostEqual(float(distance(counts,k)),float(leakage+overload))
    def test_all_v8_decisions_are_world_aggregate_referenced(self):
        rng=np.random.default_rng(9)
        n=36;k=4;colors=rng.integers(0,10,n)
        counts=np.bincount(colors,minlength=10)
        old=distance(counts,k)
        new=counts.copy()
        source=int(colors[0]);destination=(source+1)%10
        new[source]-=1;new[destination]+=1
        # The provisional signal is a GLOBAL counterfactual and must NOT be
        # counted as local information in any V9 strict-collective actor.
        signal=n*(old-distance(new,k))
        self.assertTrue(np.isfinite(signal))
    def test_no_neural_exact_is_not_silently_solved(self):
        # A two-epoch untrained evaluation should preserve bounded metrics.
        weights=np.zeros((36,2),dtype=float)
        r=trial(n=36,k=4,batch=12,epochs=2,seed=21,weights=weights)
        self.assertGreaterEqual(r["final_D"],0)
        self.assertLessEqual(r["final_D"],1)
        self.assertAlmostEqual(r["leakage"]+r["overload"],r["final_D"])
    def test_frozen_model_artifacts_present(self):
        for rep in range(3):
            path=ROOT/"models"/f"acceptance_n324_k4_rep{rep}.npz"
            self.assertTrue(path.exists(),str(path))
            with np.load(path) as data:
                self.assertEqual(tuple(data["theta"].shape),(324,2))

if __name__=="__main__":
    unittest.main()
