import json
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G37D_CORRECTED_MUTATION_PLAN"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

plan={
  "mission":MISSION,
  "mode":"PLAN_ONLY_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "status":"READY_FOR_DRY_RUN",
  "entity_mutations":[
    {
      "action":"UPDATE_ALIAS_RECONCILIATION",
      "current_name":"REINDEER MO",
      "official_abbi_name":"REINDEER",
      "registry_number":"10010628",
      "strategy":"keep existing id; update official_name to REINDEER; add REINDEER MO as alias"
    },
    {
      "action":"UPDATE_ALIAS_RECONCILIATION",
      "current_name":"110",
      "official_abbi_name":"MO 110",
      "registry_number":"10007793",
      "strategy":"keep existing id; update official_name to MO 110; add 110 as alias"
    },
    {
      "action":"CREATE_ENTITY_CANDIDATE",
      "official_name":"NACCARATO BREEDING",
      "registry_number":"21",
      "animal_type":"bull",
      "validation_status":"provisional",
      "confidence_score":85,
      "source_url":"http://members.americanbuckingbull.com/bulls.aspx?id=21"
    },
    {
      "action":"CREATE_ENTITY_CANDIDATE",
      "official_name":"DIAMOND'S GHOST",
      "registry_number":"10000789",
      "animal_type":"bull",
      "validation_status":"provisional",
      "confidence_score":85,
      "source_url":"http://members.americanbuckingbull.com/bulls.aspx?id=10007793"
    },
    {
      "action":"CREATE_ENTITY_CANDIDATE",
      "official_name":"NACCARATO'S OSCARS VELVET",
      "registry_number":"10006436",
      "animal_type":"bull",
      "validation_status":"provisional",
      "confidence_score":80,
      "source_url":"http://members.americanbuckingbull.com/bulls.aspx?id=10010628"
    },
    {
      "action":"CREATE_ENTITY_CANDIDATE",
      "official_name":"JR 34",
      "registry_number":"10002937",
      "animal_type":"bull",
      "validation_status":"provisional",
      "confidence_score":80,
      "source_url":"http://members.americanbuckingbull.com/bulls.aspx?id=10007793"
    },
    {
      "action":"CREATE_ENTITY_CANDIDATE",
      "official_name":"RATJEN BREEDING",
      "registry_number":"39",
      "animal_type":"bull",
      "validation_status":"provisional",
      "confidence_score":80,
      "source_url":"http://members.americanbuckingbull.com/bulls.aspx?id=10007793"
    }
  ],
  "edge_candidates":[
    {
      "parent":"NACCARATO BREEDING",
      "parent_abbi":"21",
      "child":"REINDEER",
      "child_abbi":"10010628",
      "relation":"sire",
      "confidence_score":85
    },
    {
      "parent":"DIAMOND'S GHOST",
      "parent_abbi":"10000789",
      "child":"MO 110",
      "child_abbi":"10007793",
      "relation":"sire",
      "confidence_score":85
    }
  ],
  "blocked_edges":[
    {
      "child":"REINDEER",
      "child_abbi":"10010628",
      "relation":"dam",
      "reason":"parent name missing; only ABBI#10004709 known"
    },
    {
      "child":"MO 110",
      "child_abbi":"10007793",
      "relation":"dam",
      "reason":"dam missing from public ABBI page"
    }
  ]
}

(out/"P56G37D_CORRECTED_MUTATION_PLAN.json").write_text(
 json.dumps(plan,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps({
 "mission":MISSION,
 "entity_mutations":len(plan["entity_mutations"]),
 "edge_candidates":len(plan["edge_candidates"]),
 "blocked_edges":len(plan["blocked_edges"]),
 "status":plan["status"]
}, indent=2))
