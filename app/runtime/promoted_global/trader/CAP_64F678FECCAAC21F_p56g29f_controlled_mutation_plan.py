import json
from pathlib import Path

out = Path("reports/P5.6G29_PEDIGREE_RECONCILIATION")
out.mkdir(parents=True, exist_ok=True)

mutation_plan = {
  "mission": "P5.6G29F_CONTROLLED_MUTATION_PLAN",
  "mode": "PLAN_ONLY_NO_DATABASE_WRITE",
  "target": "Bushwacker ABBI pedigree reconciliation",
  "preconditions": [
    "REINDEER MO absent from p55a_animals",
    "110 absent from p55a_animals",
    "Whitewater Skoal -> Bushwacker is provisional and unsourced",
    "Lady Luck -> Bushwacker is provisional and unsourced",
    "ABBI page fetched and parsed successfully"
  ],
  "planned_steps": [
    {
      "step": 1,
      "action": "INSERT_PARENT_ANIMAL_CANDIDATE",
      "table": "p55a_animals",
      "record": {
        "official_name": "REINDEER MO",
        "registry_number": "10010628",
        "animal_type": "bucking_bull",
        "sex": "male",
        "validation_status": "reliable",
        "confidence_score": 85,
        "notes": "Created from ABBI pedigree page for Bushwacker ABBI#10058008. Pending final promotion."
      }
    },
    {
      "step": 2,
      "action": "INSERT_PARENT_ANIMAL_CANDIDATE",
      "table": "p55a_animals",
      "record": {
        "official_name": "110",
        "registry_number": "10007793",
        "animal_type": "bucking_cattle",
        "sex": "female",
        "validation_status": "reliable",
        "confidence_score": 85,
        "notes": "Created from ABBI pedigree page for Bushwacker ABBI#10058008. Pending final promotion."
      }
    },
    {
      "step": 3,
      "action": "QUARANTINE_UNSOURCED_CONFLICT",
      "table": "p55a_pedigree_edges",
      "match": {
        "parent": "Whitewater Skoal",
        "child": "Bushwacker",
        "relation": "sire",
        "validation_status": "provisional",
        "evidence_source_id": None
      }
    },
    {
      "step": 4,
      "action": "QUARANTINE_UNSOURCED_CONFLICT",
      "table": "p55a_pedigree_edges",
      "match": {
        "parent": "Lady Luck",
        "child": "Bushwacker",
        "relation": "dam",
        "validation_status": "provisional",
        "evidence_source_id": None
      }
    },
    {
      "step": 5,
      "action": "INSERT_PEDIGREE_EDGE_CANDIDATE",
      "table": "p55a_pedigree_edges",
      "record": {
        "parent": "REINDEER MO",
        "child": "Bushwacker",
        "relation": "sire",
        "confidence_score": 85,
        "validation_status": "reliable",
        "evidence": "ABBI profile 10058008"
      }
    },
    {
      "step": 6,
      "action": "INSERT_PEDIGREE_EDGE_CANDIDATE",
      "table": "p55a_pedigree_edges",
      "record": {
        "parent": "110",
        "child": "Bushwacker",
        "relation": "dam",
        "confidence_score": 85,
        "validation_status": "reliable",
        "evidence": "ABBI profile 10058008"
      }
    }
  ],
  "execution_status": "NOT_EXECUTED",
  "risk": "MEDIUM",
  "requires_manual_approval": True
}

(out / "P56G29F_CONTROLLED_MUTATION_PLAN.json").write_text(
    json.dumps(mutation_plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(mutation_plan, indent=2, ensure_ascii=False))
