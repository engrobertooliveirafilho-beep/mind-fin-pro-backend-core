
import json
from datetime import datetime, timezone

TARGET_ANIMALS = [
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
]

SOURCE_TARGETS = [
    {"source_type":"ABBI_PROFILE", "query_template":"site:theabbi.com \"{animal}\" \"sire\" \"dam\""},
    {"source_type":"PBR_PROFILE", "query_template":"site:pbr.com \"{animal}\" \"sire\" \"dam\""},
    {"source_type":"SALE_CATALOG", "query_template":"\"{animal}\" \"sire\" \"dam\" \"lot\""},
    {"source_type":"SEMEN_CATALOG", "query_template":"\"{animal}\" \"sire\" \"dam\" \"semen\""},
    {"source_type":"EMBRYO_CATALOG", "query_template":"\"{animal}\" \"sire\" \"dam\" \"embryo\""},
    {"source_type":"BREEDER_REGISTRY", "query_template":"\"{animal}\" \"sire\" \"dam\" \"breeder\""}
]

def build_harvest_plan():
    queries = []
    for animal in TARGET_ANIMALS:
        for target in SOURCE_TARGETS:
            queries.append({
                "animal": animal,
                "source_type": target["source_type"],
                "query": target["query_template"].format(animal=animal),
                "status": "PENDING_SEARCH"
            })

    return {
        "mission": "P5.6G18_AUTOMATED_SOURCE_HARVESTER",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "PLAN_ONLY_NO_WEB_NO_DB_MUTATION",
        "target_animals": len(TARGET_ANIMALS),
        "planned_queries": len(queries),
        "queries": queries,
        "output_contract": {
            "animal": "required",
            "sire": "optional but at least sire or dam required",
            "dam": "optional but at least sire or dam required",
            "source_url": "required",
            "source_type": "required allowed type",
            "confidence": "minimum 60"
        }
    }

if __name__ == "__main__":
    plan = build_harvest_plan()
    open("P56G18_AUTOMATED_SOURCE_HARVEST_PLAN.json","w",encoding="utf-8").write(
        json.dumps(plan,indent=2,ensure_ascii=False)
    )
    print(json.dumps(plan,indent=2,ensure_ascii=False))
