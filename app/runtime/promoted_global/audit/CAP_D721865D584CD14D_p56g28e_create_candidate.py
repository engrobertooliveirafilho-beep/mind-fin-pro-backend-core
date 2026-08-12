import json
from pathlib import Path

candidate = {
    "animal":"Bushwacker",
    "animal_abbi":"10058008",

    "candidate_sire":"REINDEER MO",
    "candidate_sire_abbi":"10010628",

    "candidate_dam":"110",
    "candidate_dam_abbi":"10007793",

    "source_url":"http://members.americanbuckingbull.com/bulls.aspx?id=10058008",

    "evidence_type":"ABBI_PEDIGREE_PAGE",

    "status":"PENDING_RECONCILIATION",

    "conflicts_with_existing_graph": True
}

out = Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION")
out.mkdir(parents=True, exist_ok=True)

(out / "P56G28E_PEDIGREE_CANDIDATES.json").write_text(
    json.dumps([candidate], indent=2),
    encoding="utf-8"
)

print(json.dumps(candidate, indent=2))
