"""M038: query-driven academic metadata retrieval and manual claim assessment.

A catalogue hit verifies neither the scientific claim nor full-text coverage.
No automatic literature completeness or relevance score is asserted.
"""
from __future__ import annotations

import os
import re
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy

from .core import ABError, nonempty, stable_id, utc_now

ROLES = ("UNCLASSIFIED", "P0", "P1", "PX", "PM", "PN")
RELATIONS = ("supports", "contradicts", "context", "unreviewed")
PROVIDERS = ("openalex", "semanticscholar")


def make_plan(question: str, rivals: list[str] | None = None,
              cutoff_year: int | None = None) -> dict:
    question = nonempty(question, "question")
    if cutoff_year is not None and (isinstance(cutoff_year, bool)
                                   or not isinstance(cutoff_year, int)
                                   or not 1900 <= cutoff_year <= 2100):
        raise ABError("cutoff_year must be an integer between 1900 and 2100")
    rivals = rivals or []
    if any(not isinstance(r, str) or not r.strip() for r in rivals):
        raise ABError("rivals must be nonempty strings")
    searches = [
        {"id": "Q01", "purpose": "prior_art", "query": question},
        {"id": "Q02", "purpose": "adversarial", "query": question + " criticism alternative explanations"},
        {"id": "Q03", "purpose": "methodology", "query": question + " replication empirical methods"},
    ]
    for idx, rival in enumerate(rivals, start=4):
        searches.append({"id": f"Q{idx:02d}", "purpose": "rival", "query": rival.strip()})
    return {
        "schema": "AB-LITERATURE-0.1",
        "question": question,
        "cutoff_year": cutoff_year,
        "rivals": rivals,
        "queries": [{**q, "status": "planned"} for q in searches],
        "references": [],
        "retrieval": {"state": "NOT_RUN", "errors": [], "searched_at": None},
        "limitations": [
            "Search terms are heuristics; no claim of systematic completeness.",
            "Metadata matching does not validate the content of an article.",
            "Coverage of books and older non-indexed literature may be incomplete.",
        ],
    }


def _request_json(url: str, timeout: int = 15):
    import json
    headers = {"User-Agent": "AB-Literature-Pilot/0.1 (metadata-only; research)"}
    if urllib.parse.urlparse(url).hostname == "api.semanticscholar.org":
        key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        if key:
            headers["x-api-key"] = key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise ABError(f"HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _clean_doi(doi: str | None) -> str:
    if not doi:
        return ""
    doi = doi.strip().lower()
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()


def _ref_key(paper: dict) -> str:
    doi = _clean_doi(paper.get("doi"))
    if doi:
        return "doi:" + doi
    return stable_id("title", _normalize_title(paper.get("title", "")), str(paper.get("year", "")))


def search_openalex(query: str, per_page: int = 8, fetch=_request_json) -> list[dict]:
    params = urllib.parse.urlencode({
        "search": nonempty(query, "query"),
        "per-page": max(1, min(25, int(per_page))),
        "select": "id,title,publication_year,doi,authorships,primary_location,abstract_inverted_index",
    })
    data = fetch("https://api.openalex.org/works?" + params)
    out = []
    for item in data.get("results", []):
        title = item.get("title") or ""
        if not title:
            continue
        loc = item.get("primary_location") or {}
        landing = loc.get("landing_page_url") or item.get("id", "")
        out.append({
            "title": title,
            "year": item.get("publication_year"),
            "doi": _clean_doi(item.get("doi")),
            "url": landing,
            "authors": [x.get("author", {}).get("display_name", "")
                        for x in item.get("authorships", [])],
            "catalogue_id": item.get("id"),
            "source": "openalex",
        })
    return out


def search_semantic_scholar(query: str, per_page: int = 8, fetch=_request_json) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": nonempty(query, "query"),
        "limit": max(1, min(25, int(per_page))),
        "fields": "title,year,authors,externalIds,url,paperId",
    })
    data = fetch("https://api.semanticscholar.org/graph/v1/paper/search?" + params)
    out = []
    for item in data.get("data", []):
        if not item.get("title"):
            continue
        ids = item.get("externalIds") or {}
        out.append({
            "title": item["title"],
            "year": item.get("year"),
            "doi": _clean_doi(ids.get("DOI")),
            "url": item.get("url"),
            "authors": [x.get("name", "") for x in item.get("authors", [])],
            "catalogue_id": item.get("paperId"),
            "source": "semanticscholar",
        })
    return out


def register(results: list[dict]) -> list[dict]:
    """Deduplicate by DOI or normalized title/year; preserve provenance."""
    found: dict[str, dict] = {}
    for item in results:
        title = nonempty(item.get("title", ""), "paper.title")
        key = _ref_key(item)
        if key not in found:
            found[key] = {
                "id": key, "title": title, "year": item.get("year"),
                "authors": item.get("authors") or [],
                "doi": _clean_doi(item.get("doi")), "url": item.get("url") or "",
                "role": "UNCLASSIFIED", "metadata_sources": [],
            "temporal_status": item.get("temporal_status", "UNKNOWN"),
                "metadata_status": "CATALOGUED_NOT_CONTENT_VERIFIED",
                "assessments": [], "discovered_by": [],
            }
        source = item.get("source")
        source_record = {"provider": source, "catalogue_id": item.get("catalogue_id")}
        if source_record not in found[key]["metadata_sources"]:
            found[key]["metadata_sources"].append(source_record)
        query = item.get("query_id", "")
        if query and query not in found[key]["discovered_by"]:
            found[key]["discovered_by"].append(query)
    return sorted(found.values(), key=lambda r: r["id"])


def retrieve(plan: dict, providers: tuple[str, ...] = ("openalex",),
             per_query: int = 8, fetch=_request_json) -> dict:
    if plan.get("schema") != "AB-LITERATURE-0.1":
        raise ABError("Unknown literature schema")
    for provider in providers:
        if provider not in PROVIDERS:
            raise ABError("Unknown metadata provider: " + provider)
    doc = deepcopy(plan)
    entries = []
    errors = []
    excluded = []
    cutoff_year = doc.get("cutoff_year")
    for query in doc["queries"]:
        query["status"] = "searched"
        query["providers"] = {}
        for provider in providers:
            try:
                fn = search_openalex if provider == "openalex" else search_semantic_scholar
                papers = fn(query["query"], per_page=per_query, fetch=fetch)
                for paper in papers:
                    paper["query_id"] = query["id"]
                    year = paper.get("year")
                    if isinstance(year, int) and cutoff_year is not None:
                        if year > cutoff_year:
                            excluded.append({"title": paper["title"], "year": year,
                                             "reason": "AFTER_CUTOFF_YEAR",
                                             "query_id": query["id"]})
                            continue
                        paper["temporal_status"] = ("SAME_YEAR_ORDER_UNVERIFIED"
                                                    if year == cutoff_year else "BEFORE_CUTOFF_YEAR")
                    entries.append(paper)
                query["providers"][provider] = {"status": "ok", "count": len(papers)}
            except (urllib.error.URLError, ValueError, KeyError, OSError, TimeoutError) as e:
                error = {"query_id": query["id"], "provider": provider, "error": str(e)}
                errors.append(error)
                query["providers"][provider] = {"status": "error", "error": str(e)}
        if any(v["status"] == "error" for v in query["providers"].values()):
            query["status"] = "partial_or_failed"
    existing = {r["id"]: deepcopy(r) for r in doc.get("references", [])}
    for paper in register(entries):
        if paper["id"] in existing:
            old = existing[paper["id"]]
            for source in paper["metadata_sources"]:
                if source not in old["metadata_sources"]:
                    old["metadata_sources"].append(source)
            old["discovered_by"] = sorted(set(old.get("discovered_by", []) +
                                              paper["discovered_by"]))
        else:
            existing[paper["id"]] = paper
    doc["references"] = sorted(existing.values(), key=lambda r: r["id"])
    doc["retrieval"] = {
        "state": "PARTIAL" if errors else "COMPLETE_METADATA_QUERIES",
        "searched_at": utc_now(), "errors": errors,
        "excluded_after_cutoff": excluded,
    }
    return doc


def assess_reference(plan: dict, ref_id: str, claim_id: str, relationship: str,
                     passage: str, locator: str, reviewer: str, role: str | None = None) -> dict:
    if relationship not in RELATIONS:
        raise ABError(f"relationship must be one of {RELATIONS}")
    if role is not None and role not in ROLES:
        raise ABError(f"role must be one of {ROLES}")
    result = deepcopy(plan)
    for ref in result.get("references", []):
        if ref.get("id") == ref_id:
            if relationship != "unreviewed":
                for name, value in (("passage", passage), ("locator", locator),
                                    ("reviewer", reviewer), ("claim_id", claim_id)):
                    nonempty(value, name)
            item = {"claim_id": claim_id, "relationship": relationship,
                    "passage": passage, "locator": locator, "reviewer": reviewer,
                    "recorded_at": utc_now(),
                    "status": "HUMAN_OR_AGENT_ATTESTED_NOT_INDEPENDENTLY_VERIFIED"}
            ref.setdefault("assessments", []).append(item)
            if role:
                ref["role"] = role
            return result
    raise ABError(f"Reference {ref_id!r} not found")


def coverage_report(plan: dict) -> dict:
    grouped = {role: [] for role in ROLES}
    for r in plan.get("references", []):
        role = r.get("role", "UNCLASSIFIED")
        if role in grouped:
            grouped[role].append(r["id"])
    return {
        "counts_by_role": {k: len(v) for k, v in grouped.items()},
        "adversarial_references_present": bool(grouped["PX"]),
        "unassessed_references": [r["id"] for r in plan.get("references", [])
                                  if not any(a.get("relationship") != "unreviewed"
                                             for a in r.get("assessments", []))],
        "note": "Catalog coverage is unknown; no paper-count citation quota is imposed.",
    }
