"""ET665.R350 — inventory actual agent sources before any execution.

This is an evidence-only preflight: no mocks, no agent synthesis, no imports
of untrusted historical code. Missing modules remain blocked.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

CANDIDATES = (
    "business_strategy_cashflow_agent", "cognition_os_kernel_agent",
    "core_high_governance_council", "core_safety_compliance_hub",
    "core_system_supervisor", "creative_sora_marketing_director",
    "creative_video_scenarios_agent", "domain_economics_finance_markets",
    "domain_facebook_media_buyer_engine", "domain_instagram_brand_engine",
    "domain_napoleon_hill_engine", "domain_psychology_mindset",
    "domain_social_recommendation_kernel", "domain_tiktok_growth_engine",
    "domain_youtube_longform_engine", "meta_autonomous_evolution_agent",
    "meta_global_agent_mapper", "meta_mind_archives_agent_mapper",
    "mission_autonomous_docking_agent",
)

def inventory(root):
    root = Path(root).resolve()
    rows = []
    for agent in CANDIDATES:
        matches = sorted(p for p in root.rglob(agent + ".py")
                         if p.is_file() and ".git" not in p.parts)
        if not matches:
            rows.append({"agent_id": agent, "status": "MISSING_SOURCE"})
            continue
        for p in matches:
            data = p.read_bytes()
            text = data.decode("utf-8", errors="replace")
            suspicious = bool(re.search(r"not_implemented|mode\s*['\"]?\s*:\s*['\"]stub|\bNotImplementedError\b", text, re.I))
            rows.append({"agent_id": agent, "status": "STUB_SUSPECT" if suspicious else "SOURCE_FOUND_UNVERIFIED",
                         "path": str(p.relative_to(root)), "sha256": hashlib.sha256(data).hexdigest(),
                         "bytes": len(data)})
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--evidence",required=True)
    args=p.parse_args()
    rows=inventory(args.root)
    out=Path(args.evidence)
    out.mkdir(parents=True,exist_ok=True)
    summary={"status":"INVENTORY_ONLY_NOT_CERTIFIED","candidate_count":len(CANDIDATES),
             "sources_found":sum(r["status"] != "MISSING_SOURCE" for r in rows),
             "hp19_membership":"UNVERIFIED","phase_b":"NOT_CERTIFIED",
             "real_orders":"FORBIDDEN","results":rows}
    (out/"r350_agent_source_inventory.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"status":summary["status"],"sources_found":summary["sources_found"],
                      "candidate_count":len(CANDIDATES),"evidence":str(out)}))
if __name__=="__main__":
    main()
