import json
from pathlib import Path

canonical = {
  "mission": "P5.6G30B_SOURCE_DEDUP_SELECTION",
  "source_url": "http://members.americanbuckingbull.com/bulls.aspx?id=10058008",
  "duplicates_found": 4,
  "canonical_selection_rule": "highest confidence_score; if tied, earliest created_at after audit",
  "status": "NEEDS_CREATED_AT_CHECK",
  "next_step": "Query created_at for the 4 duplicate source records before selecting canonical evidence_source_id"
}

out = Path("reports/P5.6G30_CONTROLLED_PEDIGREE_MUTATION")
out.mkdir(parents=True, exist_ok=True)
(out / "P56G30B_SOURCE_DEDUP_SELECTION_PLAN.json").write_text(json.dumps(canonical, indent=2), encoding="utf-8")
print(json.dumps(canonical, indent=2))
