"""M039: typed artifact hand-offs, DAG and independent review identifiers.

Schema validation is NOT scientific validation. Agents are supplied externally;
the orchestrator does not claim to execute an LLM or to guarantee epistemic independence.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy

from .core import ABError, nonempty, require, utc_now

CONTRACTS = {
    "proposer": {"claim": str, "rivals": list, "falsifier": str},
    "designer": {"estimand": str, "comparison": str, "controls": list,
                 "falsifier": str, "prereg_ref": str},
    "implementer": {"code_commit": str, "input_hashes": dict,
                    "test_report": str, "outputs": list},
    "auditor": {"target_submission": str, "issues": list,
                "verdict": str, "independence_limits": str},
    "analyst": {"estimand": str, "results": dict, "uncertainty": dict,
                "data_refs": list},
    "librarian": {"query_log": list, "references": list, "gaps": list},
    "coordinator": {"decision": str, "alternatives": list,
                    "reason": str, "next_evidence": str},
}

DECISIONS = ("CONTINUE", "STOP", "PIVOT", "REPAIR", "BRANCH")


def new_workflow(tasks: list[dict]) -> dict:
    result = {"schema": "AB-AGENTS-0.1", "tasks": deepcopy(tasks),
              "submissions": [], "reviews": []}
    validate_workflow(result)
    return result


def validate_workflow(doc: dict) -> None:
    if doc.get("schema") != "AB-AGENTS-0.1":
        raise ABError("Unknown workflow schema")
    tasks = doc.get("tasks")
    if not isinstance(tasks, list):
        raise ABError("tasks must be list")
    by_id = {}
    for task in tasks:
        require(task, {"id": str, "role": str, "depends_on": list, "status": str}, "task")
        nonempty(task["id"], "task.id")
        if task["id"] in by_id:
            raise ABError("Duplicate task id: " + task["id"])
        if task["role"] not in CONTRACTS:
            raise ABError("Unknown role: " + task["role"])
        if task["status"] not in ("pending", "submitted", "approved", "rejected"):
            raise ABError("Invalid task status")
        by_id[task["id"]] = task
    for task in tasks:
        deps = task["depends_on"]
        if len(deps) != len(set(deps)):
            raise ABError("Repeated dependencies")
        for dep in deps:
            if dep not in by_id:
                raise ABError("Unknown dependency: " + str(dep))
            if dep == task["id"]:
                raise ABError("A task depends on itself")
    visiting, seen = set(), set()

    def walk(task_id: str):
        if task_id in visiting:
            raise ABError("Cycle in workflow DAG")
        if task_id in seen:
            return
        visiting.add(task_id)
        for dep in by_id[task_id]["depends_on"]:
            walk(dep)
        visiting.remove(task_id)
        seen.add(task_id)

    for task_id in by_id:
        walk(task_id)

    submissions = doc.get("submissions", [])
    reviews = doc.get("reviews", [])
    for submission in submissions:
        if submission.get("task_id") not in by_id:
            raise ABError("Submission without known task")
        artifact = submission.get("artifact")
        if not isinstance(artifact, dict):
            raise ABError("Submission artifact must be JSON object")
        canonical = json.dumps(artifact, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if digest != submission.get("content_sha256"):
            raise ABError("Submission hash mismatch: possible alteration after submission")
    for task in tasks:
        matching = [s for s in submissions if s.get("task_id") == task["id"]]
        if task["status"] == "pending" and matching:
            raise ABError("Pending task has an existing submission")
        if task["status"] != "pending":
            if len(matching) != 1:
                raise ABError("Non-pending task needs one immutable submission")
            if task.get("submission_sha256") != matching[0]["content_sha256"]:
                raise ABError("Task and submission hashes disagree")
        if task["status"] in ("approved", "rejected"):
            expected = "approve" if task["status"] == "approved" else "reject"
            if not any(r.get("task_id") == task["id"]
                       and r.get("verdict") == expected
                       and r.get("submission_sha256") == task["submission_sha256"]
                       for r in reviews):
                raise ABError("Approved/rejected task missing matching review")


def ready_tasks(doc: dict) -> list[dict]:
    validate_workflow(doc)
    by_id = {x["id"]: x for x in doc["tasks"]}
    return [{"id": t["id"], "role": t["role"]}
            for t in doc["tasks"]
            if t["status"] == "pending"
            and all(by_id[d]["status"] == "approved" for d in t["depends_on"])]


def validate_artifact(role: str, payload: dict) -> None:
    if role not in CONTRACTS:
        raise ABError("Unknown role")
    require(payload, CONTRACTS[role], role)
    for name, typ in CONTRACTS[role].items():
        if typ is str:
            nonempty(payload[name], f"{role}.{name}")
    if role == "proposer":
        if not payload["rivals"] or any(not isinstance(r, str) or not r.strip()
                                       for r in payload["rivals"]):
            raise ABError("Proposer requires at least one articulated rival")
    if role == "auditor" and payload["verdict"] not in ("PASS", "FAIL", "INCONCLUSIVE"):
        raise ABError("Auditor verdict not recognized")
    if role == "coordinator" and payload["decision"] not in DECISIONS:
        raise ABError("Coordinator decision not recognized")


def submit(doc: dict, task_id: str, agent_id: str, artifact: dict) -> dict:
    nonempty(agent_id, "agent_id")
    result = deepcopy(doc)
    validate_workflow(result)
    ready_ids = {t["id"] for t in ready_tasks(result)}
    if task_id not in ready_ids:
        raise ABError(f"Task {task_id} is not ready (or already submitted)")
    task = next(t for t in result["tasks"] if t["id"] == task_id)
    validate_artifact(task["role"], artifact)
    canonical = json.dumps(artifact, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    task["status"] = "submitted"
    task["submission_sha256"] = digest
    result["submissions"].append({
        "task_id": task_id, "role": task["role"], "agent_id": agent_id,
        "artifact": artifact, "content_sha256": digest, "at": utc_now(),
        "status": "SCHEMA_CHECKED_NOT_SCIENTIFICALLY_VALIDATED",
    })
    return result


def review(doc: dict, task_id: str, reviewer_id: str, verdict: str, reason: str) -> dict:
    nonempty(reviewer_id, "reviewer_id")
    nonempty(reason, "reason")
    if verdict not in ("approve", "reject"):
        raise ABError("Review must approve or reject")
    result = deepcopy(doc)
    validate_workflow(result)
    task = next((t for t in result["tasks"] if t["id"] == task_id), None)
    if not task or task["status"] != "submitted":
        raise ABError("Task not submitted")
    submission = next(s for s in reversed(result["submissions"])
                      if s["task_id"] == task_id)
    if submission["agent_id"] == reviewer_id:
        raise ABError("Self-approval forbidden")
    task["status"] = "approved" if verdict == "approve" else "rejected"
    result["reviews"].append({
        "task_id": task_id, "submission_sha256": submission["content_sha256"],
        "reviewer_id": reviewer_id, "verdict": verdict, "reason": reason,
        "at": utc_now(),
        "independence_caveat": "Different identifiers do not establish independent models or sources.",
    })
    return result
