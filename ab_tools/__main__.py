"""CLI for experimental AB M038-M042 modules. python -m ab_tools --help"""
from __future__ import annotations

import argparse
import json
import sys

from . import literature, meta_eval, orchestration, review, traceability
from .atlas_bridge import make_delta
from .core import ABError, load_json, save_json


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ab_tools",
                                     description="AB 3.2.1 experimental, non-normative tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def cmd(name):
        return sub.add_parser(name)

    def arg(p, *names, **kwargs):
        p.add_argument(*names, **kwargs)

    p = cmd("literature-plan")
    arg(p, "--question", required=True)
    arg(p, "--rival", action="append", default=[])
    arg(p, "--cutoff-year", type=int, help="Later works excluded; same-year chronology unresolved")
    arg(p, "--out", required=True)

    p = cmd("literature-search")
    arg(p, "--plan", required=True)
    arg(p, "--provider", action="append", choices=literature.PROVIDERS, default=[])
    arg(p, "--per-query", type=int, default=8)
    arg(p, "--out", required=True)

    p = cmd("literature-assess")
    arg(p, "--plan", required=True)
    arg(p, "--ref-id", required=True)
    arg(p, "--claim", required=True)
    arg(p, "--relationship", choices=literature.RELATIONS, required=True)
    arg(p, "--passage", default="")
    arg(p, "--locator", default="")
    arg(p, "--reviewer", default="")
    arg(p, "--role", choices=literature.ROLES)
    arg(p, "--out", required=True)

    p = cmd("literature-coverage")
    arg(p, "--plan", required=True)

    p = cmd("workflow-init")
    arg(p, "--tasks", required=True, help="JSON array of typed DAG tasks")
    arg(p, "--out", required=True)

    p = cmd("workflow-ready")
    arg(p, "--file", required=True)

    p = cmd("workflow-submit")
    arg(p, "--file", required=True)
    arg(p, "--task", required=True)
    arg(p, "--agent", required=True)
    arg(p, "--artifact", required=True, help="Typed JSON artifact")
    arg(p, "--out", required=True)

    p = cmd("workflow-review")
    arg(p, "--file", required=True)
    arg(p, "--task", required=True)
    arg(p, "--reviewer", required=True)
    arg(p, "--verdict", choices=("approve", "reject"), required=True)
    arg(p, "--reason", required=True)
    arg(p, "--out", required=True)

    p = cmd("claims-init")
    arg(p, "--out", required=True)

    p = cmd("claims-add")
    arg(p, "--file", required=True)
    arg(p, "--id", required=True)
    arg(p, "--text", required=True)
    arg(p, "--scope", default="")
    arg(p, "--out", required=True)

    p = cmd("evidence-file")
    arg(p, "--file", required=True)
    arg(p, "--id", required=True)
    arg(p, "--path", required=True)
    arg(p, "--root", default=".")
    arg(p, "--kind", default="analysis")
    arg(p, "--out", required=True)

    p = cmd("evidence-url")
    arg(p, "--file", required=True)
    arg(p, "--id", required=True)
    arg(p, "--url", required=True)
    arg(p, "--kind", default="publication")
    arg(p, "--sha256", default="")
    arg(p, "--out", required=True)

    p = cmd("claims-link")
    arg(p, "--file", required=True)
    arg(p, "--claim", required=True)
    arg(p, "--evidence", required=True)
    arg(p, "--relationship", choices=traceability.RELATIONS, required=True)
    arg(p, "--locator", default="")
    arg(p, "--reviewer", default="")
    arg(p, "--note", default="")
    arg(p, "--out", required=True)

    p = cmd("claims-audit")
    arg(p, "--file", required=True)
    arg(p, "--root", default=".")

    p = cmd("atlas-export")
    arg(p, "--claims", required=True)
    arg(p, "--batch", required=True)
    arg(p, "--parent-batch", default="")
    arg(p, "--parent-node", default="root")
    arg(p, "--mode", choices=("research", "hybrid", "meta"), default="research")
    arg(p, "--out", required=True)

    p = cmd("review-compare")
    arg(p, "--before", required=True)
    arg(p, "--after", required=True)
    arg(p, "--scientific-audit", required=True)
    arg(p, "--reviewer", required=True)
    arg(p, "--out", required=True)

    p = cmd("meta-compare")
    arg(p, "--rows", required=True)
    arg(p, "--baseline", default="baseline")
    arg(p, "--candidate", default="ab")
    arg(p, "--draws", type=int, default=2000)
    arg(p, "--out", required=True)

    p = cmd("meta-ablations")
    arg(p, "--rows", required=True)
    arg(p, "--baseline", default="baseline")
    arg(p, "--draws", type=int, default=2000)
    arg(p, "--out", required=True)

    a = parser.parse_args(argv)
    try:
        if a.cmd == "literature-plan":
            result = literature.make_plan(a.question, a.rival, a.cutoff_year)
        elif a.cmd == "literature-search":
            result = literature.retrieve(load_json(a.plan),
                                         tuple(a.provider or ["openalex"]), a.per_query)
        elif a.cmd == "literature-assess":
            result = literature.assess_reference(
                load_json(a.plan), a.ref_id, a.claim, a.relationship,
                a.passage, a.locator, a.reviewer, a.role)
        elif a.cmd == "literature-coverage":
            result = literature.coverage_report(load_json(a.plan))
        elif a.cmd == "workflow-init":
            result = orchestration.new_workflow(load_json(a.tasks))
        elif a.cmd == "workflow-ready":
            result = {"ready": orchestration.ready_tasks(load_json(a.file))}
        elif a.cmd == "workflow-submit":
            result = orchestration.submit(load_json(a.file), a.task,
                                          a.agent, load_json(a.artifact))
        elif a.cmd == "workflow-review":
            result = orchestration.review(load_json(a.file), a.task,
                                          a.reviewer, a.verdict, a.reason)
        elif a.cmd == "claims-init":
            result = traceability.new_ledger()
        elif a.cmd == "claims-add":
            result = traceability.add_claim(load_json(a.file), a.id, a.text, a.scope)
        elif a.cmd == "evidence-file":
            result = traceability.add_file_evidence(load_json(a.file),
                                                     a.id, a.path, a.root, a.kind)
        elif a.cmd == "evidence-url":
            result = traceability.add_external_evidence(load_json(a.file),
                                                        a.id, a.url, a.kind, a.sha256)
        elif a.cmd == "claims-link":
            result = traceability.link(load_json(a.file), a.claim, a.evidence,
                                       a.relationship, a.locator, a.reviewer, a.note)
        elif a.cmd == "claims-audit":
            result = traceability.audit(load_json(a.file), a.root)
        elif a.cmd == "atlas-export":
            result = make_delta(load_json(a.claims), a.batch, a.parent_batch,
                                a.parent_node, a.mode)
        elif a.cmd == "review-compare":
            result = review.compare_editorial(load_json(a.before), load_json(a.after),
                                              load_json(a.scientific_audit), a.reviewer)
        elif a.cmd == "meta-compare":
            result = meta_eval.compare(load_json(a.rows), a.baseline,
                                       a.candidate, draws=a.draws)
        elif a.cmd == "meta-ablations":
            result = meta_eval.compare_ablations(load_json(a.rows),
                                                 a.baseline, draws=a.draws)
        else:
            raise ABError("Unknown command")
        if hasattr(a, "out"):
            save_json(a.out, result)
            print(a.out)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ABError, ValueError, KeyError, OSError, TypeError) as exc:
        print("AB_TOOL_ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
