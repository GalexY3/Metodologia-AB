"""Precommitted independent engineering checks; no original ESBM run."""
import unittest
from survival_metrics import km_rmst, from_esbm_histories


class SurvivalMetricsContract(unittest.TestCase):
    def test_two_events_two_admin_censor(self):
        r = km_rmst([1, 2, 4, 4], [1, 1, 0, 0], 4)
        self.assertAlmostEqual(r["rmst"], 2.75)
        self.assertEqual((r["events"], r["censored"]), (2, 2))
        self.assertAlmostEqual(r["completed_only_mean"], 1.5)

    def test_censor_competes_with_events(self):
        r = km_rmst([1, 2, 4, 4], [0, 1, 0, 0], 4)
        self.assertAlmostEqual(r["rmst"], 10 / 3)
        self.assertEqual(r["events"], 1)

    def test_none_dissolve(self):
        r = from_esbm_histories([], [4, 4, 4], 4)
        self.assertEqual(r["rmst"], 4)
        self.assertIsNone(r["completed_only_mean"])

    def test_all_dissolve_immediately(self):
        r = from_esbm_histories([1, 1, 1], [], 4)
        self.assertEqual(r["rmst"], 1)
        self.assertAlmostEqual(r["completed_only_mean"], 1)

    def test_risk_event_and_censor_tie(self):
        r = km_rmst([1, 1, 4], [1, 0, 0], 4)
        self.assertAlmostEqual(r["rmst"], 3)

    def test_invalid_flags(self):
        with self.assertRaises(ValueError):
            km_rmst([1, 4], [True, 0], 4)

    def test_event_at_horizon_invalid(self):
        with self.assertRaises(ValueError):
            km_rmst([4], [1], 4)

    def test_no_followup_to_horizon(self):
        with self.assertRaises(ValueError):
            km_rmst([1, 2], [0, 0], 4)

    def test_adapter_vs_direct(self):
        a = from_esbm_histories([1, 2], [4, 4], 4)
        b = km_rmst([1, 2, 4, 4], [1, 1, 0, 0], 4)
        self.assertEqual(a, b)

if __name__ == "__main__":
    unittest.main(verbosity=2)
