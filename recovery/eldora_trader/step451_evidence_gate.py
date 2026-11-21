"""STEP451: evidence-scored branch selection, offline and fail-closed.

This is an opt-in correction; it does not mount routes or replace legacy sources.
"""
from __future__ import annotations
import math

class EvidenceRejected(ValueError):
    pass

def rank_branches(branches, assessments):
    """Assessments are externally supplied, independently evaluated scores [0,1].
    No positional scoring, generated reasoning, or synthetic assessment.
    """
    if not isinstance(branches, list) or not branches:
        raise EvidenceRejected("branches required")
    if not isinstance(assessments, dict):
        raise EvidenceRejected("assessments required")
    ids = []
    for branch in branches:
        if not isinstance(branch, dict) or not isinstance(branch.get("branch_id"), str) or not branch["branch_id"].strip():
            raise EvidenceRejected("invalid branch")
        ids.append(branch["branch_id"])
    if len(set(ids)) != len(ids) or set(ids) != set(assessments):
        raise EvidenceRejected("duplicate branch or missing/extra assessment")
    ranked = []
    for branch in branches:
        key = branch["branch_id"]
        entry = assessments[key]
        if not isinstance(entry, dict) or entry.get("verified") is not True:
            raise EvidenceRejected("independent verification required")
        score = entry.get("score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1:
            raise EvidenceRejected("invalid score")
        evidence = entry.get("evidence_id")
        if not isinstance(evidence, str) or not evidence.strip():
            raise EvidenceRejected("traceable evidence required")
        ranked.append({"branch_id": key, "score": float(score), "evidence_id": evidence})
    return sorted(ranked, key=lambda x: (-x["score"], x["branch_id"]))
