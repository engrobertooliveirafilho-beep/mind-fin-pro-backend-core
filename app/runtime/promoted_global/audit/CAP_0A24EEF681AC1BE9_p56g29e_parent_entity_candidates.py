import json
from pathlib import Path

out = Path("reports/P5.6G29_PEDIGREE_RECONCILIATION")
out.mkdir(parents=True, exist_ok=True)

candidates = [
  {
    "official_name": "REINDEER MO",
    "registry_number": "10010628",
    "animal_type": "bucking_bull",
    "sex": "male",
    "validation_status": "candidate",
    "confidence_score": 85,
    "source_url": "http://members.americanbuckingbull.com/bulls.aspx?id=10058008",
    "evidence_type": "ABBI_PEDIGREE_PAGE",
    "action": "CREATE_CANDIDATE_PARENT_ENTITY"
  },
  {
    "official_name": "110",
    "registry_number": "10007793",
    "animal_type": "bucking_cattle",
    "sex": "female",
    "validation_status": "candidate",
    "confidence_score": 85,
    "source_url": "http://members.americanbuckingbull.com/bulls.aspx?id=10058008",
    "evidence_type": "ABBI_PEDIGREE_PAGE",
    "action": "CREATE_CANDIDATE_PARENT_ENTITY"
  }
]

(out / "P56G29E_PARENT_ENTITY_CANDIDATES.json").write_text(
    json.dumps(candidates, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(candidates, indent=2, ensure_ascii=False))
