"""Tests for M038-M042: local synthetic fixtures, no scientific experiments."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ab_tools import literature, meta_eval, orchestration, review, traceability
from ab_tools.atlas_bridge import make_delta
from ab_tools.core import ABError, content_sha256, load_json, save_json

ROOT = Path(__file__).resolve().parents[1]


class LiteratureTests(unittest.TestCase):
    def test_plans_include_adversarial_queries(self):
        plan = literature.make_plan("cooperation MARL", ["assortment effects"])
        self.assertEqual(len(plan["queries"]), 4)
        self.assertIn("adversarial", [q["purpose"] for q in plan["queries"]])
        self.assertEqual(plan["retrieval"]["state"], "NOT_RUN")

    def test_metadata_dedup_and_assessment(self):
        def fake(url):
            if "openalex" in url:
                return {"results": [{
                    "id": "https://openalex.org/W123", "title": "A Study",
                    "publication_year": 2023, "doi": "https://doi.org/10.1234/abc",
                    "authorships": [{"author": {"display_name": "Researcher"}}],
                    "primary_location": {"landing_page_url": "https://example.org/paper"},
                }]}
            return {"data": [{
                "paperId": "S123", "title": "A Study", "year": 2023,
                "externalIds": {"DOI": "10.1234/abc"},
                "authors": [{"name": "Researcher"}],
                "url": "https://example.org/paper",
            }]}
        plan = literature.retrieve(
            literature.make_plan("social systems"),
            providers=("openalex", "semanticscholar"), fetch=fake)
        self.assertEqual(len(plan["references"]), 1)
        self.assertEqual(len(plan["references"][0]["metadata_sources"]), 2)
        self.assertIn("NOT_CONTENT_VERIFIED", plan["references"][0]["metadata_status"])
        self.assertEqual(plan["references"][0]["role"], "UNCLASSIFIED")
        rid = plan["references"][0]["id"]
        with self.assertRaises(ABError):
            literature.assess_reference(plan, rid, "C1", "supports", "", "", "")
        with_assessment = literature.assess_reference(
            plan, rid, "C1", "contradicts", "Contrary evidence",
            "section 2", "auditor", role="PX")
        coverage = literature.coverage_report(with_assessment)
        self.assertEqual(coverage["counts_by_role"]["PX"], 1)
        self.assertTrue(coverage["adversarial_references_present"])

    def test_cutoff_excludes_future_and_preserves_ambiguity(self):
        def fake(_):
            return {"results": [
                {"title": "Older", "publication_year": 2022, "doi": "10.0/old"},
                {"title": "Same Year", "publication_year": 2024, "doi": "10.0/same"},
                {"title": "Future", "publication_year": 2026, "doi": "10.0/future"},
            ]}
        plan = literature.retrieve(literature.make_plan("topic", cutoff_year=2024),
                                   fetch=fake)
        self.assertEqual(len(plan["references"]), 2)
        self.assertEqual(plan["references"][-1]["temporal_status"],
                         "SAME_YEAR_ORDER_UNVERIFIED")
        self.assertEqual(len(plan["retrieval"]["excluded_after_cutoff"]), 3)

    def test_network_failure_recorded(self):
        def broken(_):
            raise OSError("network unavailable")
        result = literature.retrieve(
            literature.make_plan("one topic"), fetch=broken)
        self.assertEqual(result["retrieval"]["state"], "PARTIAL")
        self.assertEqual(len(result["retrieval"]["errors"]), 3)
        self.assertEqual(len(result["references"]), 0)

    def test_no_forced_citation_count(self):
        doc = literature.make_plan("sociology")
        self.assertIn("no paper-count citation quota",
                      literature.coverage_report(doc)["note"])


class OrchestrationTests(unittest.TestCase):
    @staticmethod
    def workflow():
        return orchestration.new_workflow([
            {"id": "hyp", "role": "proposer", "depends_on": [], "status": "pending"},
            {"id": "design", "role": "designer", "depends_on": ["hyp"],
             "status": "pending"},
        ])

    def test_dependency_and_manual_review(self):
        doc = self.workflow()
        self.assertEqual([x["id"] for x in orchestration.ready_tasks(doc)], ["hyp"])
        doc = orchestration.submit(doc, "hyp", "writer", {
            "claim": "H", "rivals": ["null"], "falsifier": "test",
        })
        self.assertEqual(orchestration.ready_tasks(doc), [])
        with self.assertRaises(ABError):
            orchestration.review(doc, "hyp", "writer", "approve", "self-review")
        doc = orchestration.review(doc, "hyp", "independent-id", "approve", "schema ok")
        self.assertEqual([x["id"] for x in orchestration.ready_tasks(doc)], ["design"])
        self.assertEqual(doc["submissions"][0]["status"],
                         "SCHEMA_CHECKED_NOT_SCIENTIFICALLY_VALIDATED")

    def test_tampered_submission_is_detected(self):
        doc = self.workflow()
        doc = orchestration.submit(doc, "hyp", "author", {
            "claim": "H", "rivals": ["null"], "falsifier": "test",
        })
        doc["submissions"][0]["artifact"]["claim"] = "H tampered"
        with self.assertRaises(ABError):
            orchestration.ready_tasks(doc)

    def test_reject_blocks_next(self):
        doc = self.workflow()
        doc = orchestration.submit(doc, "hyp", "one", {
            "claim": "H", "rivals": ["null"], "falsifier": "test",
        })
        doc = orchestration.review(doc, "hyp", "two", "reject", "inadequate")
        self.assertEqual(orchestration.ready_tasks(doc), [])

    def test_dag_cycle_rejected(self):
        with self.assertRaises(ABError):
            orchestration.new_workflow([
                {"id": "a", "role": "proposer", "depends_on": ["b"],
                 "status": "pending"},
                {"id": "b", "role": "designer", "depends_on": ["a"],
                 "status": "pending"},
            ])

    def test_missing_rival_contract(self):
        with self.assertRaises(ABError):
            orchestration.validate_artifact("proposer", {
                "claim": "test", "rivals": [], "falsifier": "f",
            })


class TraceTests(unittest.TestCase):
    def test_integrity_and_revision(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "result.json"
            p.write_text('{"estimate":2.5}', encoding="utf-8")
            doc = traceability.new_ledger()
            doc = traceability.add_claim(doc, "C1", "A conditional test result")
            doc = traceability.add_file_evidence(doc, "E1", "result.json", td)
            doc = traceability.link(doc, "C1", "E1", "supports",
                                    "estimate", "auditor")
            out = traceability.audit(doc, td)
            self.assertEqual(out["evidence_integrity"]["E1"],
                             "HASH_MATCH_CONTENT_NOT_AUDITED")
            self.assertEqual(out["claims"][0]["state"], "ATTESTED_SUPPORT_NOT_VERIFIED")
            p.write_text('{"estimate":3}', encoding="utf-8")
            out = traceability.audit(doc, td)
            self.assertEqual(out["claims"][0]["state"], "BROKEN_EVIDENCE")

    def test_contradiction_requires_review(self):
        doc = traceability.new_ledger()
        doc = traceability.add_claim(doc, "C1", "Hypothesis")
        doc = traceability.add_external_evidence(doc, "E1", "https://example.org/article")
        with self.assertRaises(ABError):
            traceability.link(doc, "C1", "E1", "contradicts")
        doc = traceability.link(doc, "C1", "E1", "contradicts",
                                "abstract", "reviewer")
        self.assertEqual(traceability.audit(doc)["claims"][0]["state"],
                         "CONFLICT_NEEDS_REVIEW")

    def test_reject_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "inside"
            p.mkdir()
            (Path(td) / "outside").write_text("data", encoding="utf-8")
            with self.assertRaises(ABError):
                traceability.add_file_evidence(
                    traceability.new_ledger(), "E1", "../outside", p)

    def test_atlas_batch_uses_unreviewed_nodes(self):
        sys.path.insert(0, str(ROOT / "ab_atlas"))
        import abmap
        import atlas_delta
        doc = traceability.new_ledger()
        doc = traceability.add_claim(doc, "C1", "An uncertain claim")
        doc = traceability.add_external_evidence(doc, "E1", "https://example.org")
        doc = traceability.link(doc, "C1", "E1", "supports", "page 4", "agent")
        batch = make_delta(doc, "pilot-0001")
        atlas_delta.batch_check(batch)
        base = abmap.init_doc("Pilot", mode="research")
        for i, op in enumerate(batch["ops"]):
            atlas_delta.apply_one(base, batch, i, op)
        self.assertEqual(abmap.validate(base, strict=True), [])
        self.assertTrue(any(n["status"] == "unreviewed" for n in base["nodes"]))
        self.assertFalse(any(n["status"] == "validated" for n in base["nodes"]))


class ReviewTests(unittest.TestCase):
    @staticmethod
    def audit():
        return {"reviewer_id": "scientist", "checks": {
            name: {"status": "PASS", "evidence_ref": "audit://test/" + name}
            for name in review.MANDATORY_GATES
        }}

    def test_separation_and_quality_gates(self):
        before = {"text": r"We observed 2.5 in \cite{x}.",
                  "frozen_claims": [{"id": "C1", "value": 2.5}],
                  "author_id": "writer"}
        after = {"text": r"In the study, 2.5 was observed \cite{x}.",
                 "frozen_claims": [{"id": "C1", "value": 2.5}],
                 "author_id": "writer"}
        self.assertEqual(review.compare_editorial(
            before, after, self.audit(), "editor")["verdict"],
            "EDITORIAL_REVIEW_POSSIBLE")
        after["frozen_claims"][0]["value"] = 9.0
        self.assertEqual(review.compare_editorial(
            before, after, self.audit(), "editor")["verdict"],
            "REJECT_EDITORIAL_REVISION")

    def test_uncertain_science_blocks_editorial(self):
        audit = self.audit()
        audit["checks"]["leakage_and_selection"] = {"status": "UNKNOWN"}
        doc = {"text": "No numbers", "frozen_claims": [], "author_id": "writer"}
        self.assertEqual(review.compare_editorial(
            doc, doc, audit, "editor")["verdict"], "NEEDS_SCIENTIFIC_AUDIT")

    def test_numeric_change_is_flagged(self):
        doc = {"text": "Effect 2.0", "frozen_claims": [], "author_id": "writer"}
        revised = {**doc, "text": "Effect 3.0"}
        result = review.compare_editorial(doc, revised, self.audit(), "editor")
        self.assertIn("numeric_tokens_changed", result["flags"])

    def test_scientific_self_approval_rejected(self):
        with self.assertRaises(ABError):
            review.scientific_gate(self.audit(), "scientist")


class MetaTests(unittest.TestCase):
    @staticmethod
    def rows():
        records = []
        for case in ["A", "B", "C"]:
            for arm, score in [("baseline", 0.25), ("ab", 0.75)]:
                for replicate in [0, 1]:
                    records.append({
                        "case_id": case, "arm": arm, "replicate": replicate,
                        "score": score, "cost_seconds": 10.0,
                        "status": "success", "blind_id": f"{case}:{arm}:{replicate}",
                        "model_version": "same-model", "budget_id": "same-budget",
                    })
        return records

    def test_paired_estimate_and_uncertainty(self):
        report = meta_eval.compare(self.rows(), draws=500)
        self.assertEqual(report["n_independent_cases"], 3)
        self.assertAlmostEqual(report["difference_candidate_minus_baseline"], .5)
        self.assertEqual(report["bootstrap_95_percentile_ci"], [.5, .5])
        self.assertIn("SMALL_EXPLORATORY_PILOT", report["warnings"])

    def test_missing_arm_rejected(self):
        rows = [r for r in self.rows() if not
                (r["case_id"] == "C" and r["arm"] == "ab")]
        with self.assertRaises(ABError):
            meta_eval.compare(rows)

    def test_duplicate_run_rejected(self):
        rows = self.rows()
        with self.assertRaises(ABError):
            meta_eval.compare(rows + [rows[0]])

    def test_model_mismatch_reported(self):
        rows = self.rows()
        rows[0]["model_version"] = "different-model"
        self.assertIn("MODEL_VERSION_MISMATCH",
                      meta_eval.compare(rows)["warnings"])

    def test_failure_scored_zero(self):
        rows = self.rows()
        rows[0]["status"] = "timeout"
        rows[0]["score"] = 0.0
        self.assertEqual(meta_eval.compare(rows)["n_independent_cases"], 3)
        rows[0]["score"] = 0.9
        with self.assertRaises(ABError):
            meta_eval.compare(rows)

    def test_ablation_comparisons(self):
        rows = self.rows()
        extra = [{**r, "arm": "ab_without_lit",
                  "blind_id": "other-" + r["blind_id"], "score": .5}
                 for r in rows if r["arm"] == "ab"]
        result = meta_eval.compare_ablations(rows + extra, draws=500)
        self.assertEqual(set(result["comparisons"]), {"ab", "ab_without_lit"})


class CLITests(unittest.TestCase):
    def test_cli_creates_plan_and_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            plan, ledger = Path(td) / "plan.json", Path(td) / "claims.json"
            for args in [
                ["literature-plan", "--question", "cooperation mechanisms",
                 "--out", str(plan)],
                ["claims-init", "--out", str(ledger)],
            ]:
                cp = subprocess.run([sys.executable, "-m", "ab_tools", *args],
                                    cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(cp.returncode, 0, cp.stderr)
            self.assertEqual(load_json(plan)["schema"], "AB-LITERATURE-0.1")
            self.assertEqual(load_json(ledger)["schema"], "AB-CLAIMS-0.1")


if __name__ == "__main__":
    unittest.main()
