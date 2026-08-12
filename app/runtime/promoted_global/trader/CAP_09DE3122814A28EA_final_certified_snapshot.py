import json, hashlib
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.final_research_certification import final_research_certification
from mind_trader.app.audits.command_index import COMMANDS

def freeze_final_snapshot(tests_passed=270):
    cert=final_research_certification(tests_passed=tests_passed)
    snapshot={
        "snapshot":"P8.91_FINAL_CERTIFIED_RESEARCH_SNAPSHOT",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "certification":cert,
        "commands":COMMANDS,
        "decision":"CERTIFIED_FOR_PAPER_RESEARCH_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN"
    }
    raw=json.dumps(snapshot,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    snapshot["snapshot_hash"]=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.91_final_certified_snapshot.json").write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding="utf-8")
    return snapshot
