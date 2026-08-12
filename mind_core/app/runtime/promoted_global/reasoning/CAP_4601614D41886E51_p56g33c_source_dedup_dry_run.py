import json
from pathlib import Path
from datetime import datetime, timezone

src = Path("reports/P5.6G33B_SEMANTIC_CANONICAL_SOURCE_SELECTION/P56G33B_SEMANTIC_CANONICAL_SELECTION_PLAN.json")

plans = json.loads(src.read_text(encoding="utf-8"))

out = Path("reports/P5.6G33_SOURCE_DEDUP_CANONICALIZATION")
out.mkdir(parents=True, exist_ok=True)

updates = []
blocked = []
protected = set()

for group in plans:
    canonical = group["canonical_source_id"]
    protected.add(canonical)

for group in plans:
    canonical = group["canonical_source_id"]

    for dup in group["duplicate_source_ids"]:
        # nunca marcar canônico como duplicata
        if dup == canonical:
            blocked.append({
                "source_url": group["source_url"],
                "source_id": dup,
                "reason": "DUPLICATE_EQUALS_CANONICAL"
            })
            continue

        updates.append({
            "source_id": dup,
            "source_url": group["source_url"],
            "canonical_source_id": canonical,
            "planned_status": "duplicate_candidate",
            "execution_status": "NOT_EXECUTED"
        })

summary = {
    "mission": "P5.6G33C_SOURCE_DEDUP_DRY_RUN",
    "mode": "PLAN_ONLY_NO_DATABASE_WRITE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "duplicate_groups": len(plans),
    "planned_duplicate_updates": len(updates),
    "blocked_items": len(blocked),
    "status": "PASS" if not blocked else "REVIEW_REQUIRED"
}

(out / "P56G33C_SOURCE_DEDUP_DRY_RUN_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

(out / "P56G33C_SOURCE_DEDUP_DRY_RUN_UPDATES.json").write_text(
    json.dumps(updates, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

(out / "P56G33C_SOURCE_DEDUP_DRY_RUN_BLOCKED.json").write_text(
    json.dumps(blocked, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(summary, indent=2, ensure_ascii=False))

# Bushwacker ABBI focus
for u in updates:
    if u["source_url"] == "http://members.americanbuckingbull.com/bulls.aspx?id=10058008":
        print(u)
