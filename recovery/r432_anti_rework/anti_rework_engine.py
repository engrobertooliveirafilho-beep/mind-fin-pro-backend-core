"""MIND Anti-Retrabalho Engine v1: deterministic, offline, fail-closed gate."""
from __future__ import annotations
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

SHA = re.compile(r'^[a-fA-F0-9]{64}$')

@dataclass(frozen=True)
class Decision:
    status: str
    reason: str
    matching_ids: tuple[str, ...] = ()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_record(record: dict) -> bool:
    return (isinstance(record, dict) and isinstance(record.get('id'), str)
            and bool(record['id'].strip()) and isinstance(record.get('capability'), str)
            and bool(record['capability'].strip()) and isinstance(record.get('sha256'), str)
            and bool(SHA.fullmatch(record['sha256']))
            and isinstance(record.get('commit'), str) and bool(record['commit'].strip())
            and isinstance(record.get('tests_passed'), bool)
            and isinstance(record.get('evidence'), list)
            and all(isinstance(x, str) and x.strip() for x in record['evidence']))


def assess(candidate: dict, inventory: list[dict] | None, *, source_verified: bool = False) -> Decision:
    if inventory is None or not isinstance(inventory, list) or not all(_valid_record(x) for x in inventory):
        return Decision('BLOCK', 'INVENTORY_UNVERIFIED')
    if not _valid_record(candidate):
        return Decision('BLOCK', 'CANDIDATE_INCOMPLETE')
    ids = [x['id'] for x in inventory]
    if len(ids) != len(set(ids)):
        return Decision('BLOCK', 'INVENTORY_CONFLICT')
    hash_matches = [x for x in inventory if x['sha256'].lower() == candidate['sha256'].lower()]
    if hash_matches:
        return Decision('REUSE', 'EXACT_SHA256_MATCH', tuple(x['id'] for x in hash_matches))
    cap_matches = [x for x in inventory if x['capability'].strip().casefold() == candidate['capability'].strip().casefold()]
    if cap_matches:
        return Decision('BLOCK', 'CAPABILITY_EXISTS_REVIEW_DIFF', tuple(x['id'] for x in cap_matches))
    if not source_verified:
        return Decision('BLOCK', 'SOURCE_AUTHORITY_UNVERIFIED')
    if not candidate['tests_passed'] or not candidate['evidence']:
        return Decision('BLOCK', 'TEST_EVIDENCE_MISSING')
    return Decision('ALLOW_STAGING', 'NOVEL_VERIFIED_CANDIDATE')


def run(candidate_path: Path, inventory_path: Path, output_path: Path, source_verified: bool = False) -> Decision:
    try:
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
        result = assess(candidate, inventory, source_verified=source_verified)
    except (OSError, ValueError, TypeError):
        result = Decision('BLOCK', 'INPUT_UNREADABLE')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-verified', action='store_true')
    a = p.parse_args()
    result = run(a.candidate, a.inventory, a.output, a.source_verified)
    print(json.dumps(asdict(result)))
    raise SystemExit(0 if result.status in ('REUSE', 'ALLOW_STAGING') else 2)
