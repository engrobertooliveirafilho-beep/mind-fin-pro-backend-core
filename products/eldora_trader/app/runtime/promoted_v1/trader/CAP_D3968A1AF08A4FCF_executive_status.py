import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.transfer_snapshot import build_transfer_snapshot

def build_executive_status(tests_passed=157):
    snap=build_transfer_snapshot(tests_passed)
    return {
        "report":"P8.58_EXECUTIVE_STATUS_REPORT",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "validated_range":"P8.26-P8.57",
        "decision":"PAPER_RESEARCH_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN",
        "reproduce_tests_command":"$env:PYTHONPATH=(Get-Location).Path; pytest .\\mind_trader\\tests -q",
        "snapshot_hash":snap["snapshot_hash"]
    }

def save_executive_status_reports(
    tests_passed=157,
    json_path="mind_trader/reports/P8.58_executive_status.json",
    md_path="mind_trader/reports/P8.58_executive_status.md"
):
    r=build_executive_status(tests_passed)

    Path(json_path).parent.mkdir(parents=True,exist_ok=True)

    Path(json_path).write_text(
        json.dumps(r,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )

    md=(
        "# P8.58 Executive Status Report\n\n"
        f"- Tests passed: {r['tests_passed']}\n"
        f"- Validated range: {r['validated_range']}\n"
        f"- Decision: {r['decision']}\n"
        f"- Production: {r['production']}\n"
        f"- Live: {r['live']}\n"
        f"- Edge claim: {r['edge_claim']}\n"
        f"- Causality claim: {r['causality_claim']}\n"
        f"- Snapshot hash: {r['snapshot_hash']}\n\n"
        "## Reproduce\n\n"
        f"{r['reproduce_tests_command']}\n"
    )

    Path(md_path).write_text(md,encoding="utf-8")

    return r
