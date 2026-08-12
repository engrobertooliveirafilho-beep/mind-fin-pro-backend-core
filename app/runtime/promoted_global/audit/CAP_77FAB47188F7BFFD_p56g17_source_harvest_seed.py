import json
from datetime import datetime, timezone

records = {
  "mission": "P5.6G17_REAL_SOURCE_HARVEST_SEED_LIST",
  "created_at": datetime.now(timezone.utc).isoformat(),
  "mode": "SOURCE_TARGET_LIST_NO_DB_MUTATION",
  "target_animals": [
    "Bushwacker",
    "Bodacious",
    "SweetPro's Bruiser",
    "Woopaa",
    "Little Yellow Jacket",
    "Long John",
    "Air Time",
    "Smooth Operator",
    "Mossy Oak Mudslinger",
    "Chicken on a Chain"
  ],
  "source_queries": [
    "site:theabbi.com Bushwacker sire dam",
    "site:pbr.com Bushwacker sire dam",
    "site:theabbi.com Bodacious sire dam",
    "site:pbr.com Bodacious sire dam",
    "\"SweetPro's Bruiser\" sire dam",
    "\"Woopaa\" sire dam",
    "\"Little Yellow Jacket\" sire dam",
    "\"Long John\" bucking bull sire dam",
    "\"Air Time\" bucking bull sire dam",
    "\"Smooth Operator\" bucking bull sire dam"
  ],
  "accepted_source_types": [
    "ABBI_PROFILE",
    "PBR_PROFILE",
    "SALE_CATALOG",
    "SEMEN_CATALOG",
    "EMBRYO_CATALOG",
    "BREEDER_REGISTRY"
  ],
  "rejection_rules": [
    "search snippets are not evidence",
    "blog text without explicit sire/dam is rejected",
    "human names are rejected as animals",
    "weak parent is rejected",
    "source_url is mandatory",
    "confidence must be >= 60"
  ]
}

open("P56G17_REAL_SOURCE_HARVEST_SEED_LIST.json","w",encoding="utf-8").write(
    json.dumps(records,indent=2,ensure_ascii=False)
)

print(json.dumps(records,indent=2,ensure_ascii=False))
