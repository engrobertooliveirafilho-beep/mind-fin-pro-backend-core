import json
from pathlib import Path

out = Path("reports/P5.6G29_PEDIGREE_RECONCILIATION")
out.mkdir(parents=True, exist_ok=True)

ledger = {
  "mission": "P5.6G29_PEDIGREE_RECONCILIATION",
  "animal": "Bushwacker",
  "animal_abbi": "10058008",
  "status": "RECONCILIATION_REQUIRED",
  "current_graph_edges": [
    {
      "relation": "sire",
      "parent": "Whitewater Skoal",
      "child": "Bushwacker",
      "confidence": 60,
      "validation_status": "provisional",
      "source": None,
      "classification": "PROVISIONAL_UNSOURCED_CONFLICT"
    },
    {
      "relation": "dam",
      "parent": "Lady Luck",
      "child": "Bushwacker",
      "confidence": 60,
      "validation_status": "provisional",
      "source": None,
      "classification": "PROVISIONAL_UNSOURCED_CONFLICT"
    }
  ],
  "abbi_candidate_edges": [
    {
      "relation": "sire",
      "parent": "REINDEER MO",
      "parent_abbi": "10010628",
      "child": "Bushwacker",
      "child_abbi": "10058008",
      "source_url": "http://members.americanbuckingbull.com/bulls.aspx?id=10058008",
      "evidence_type": "ABBI_PEDIGREE_PAGE",
      "classification": "HIGH_EVIDENCE_CANDIDATE"
    },
    {
      "relation": "dam",
      "parent": "110",
      "parent_abbi": "10007793",
      "child": "Bushwacker",
      "child_abbi": "10058008",
      "source_url": "http://members.americanbuckingbull.com/bulls.aspx?id=10058008",
      "evidence_type": "ABBI_PEDIGREE_PAGE",
      "classification": "HIGH_EVIDENCE_CANDIDATE"
    }
  ],
  "decision": "DO_NOT_PROMOTE_YET",
  "next_required_step": "Create or resolve parent animal records for REINDEER MO and 110, then quarantine/retire unsourced provisional conflicts before promotion."
}

(out / "P56G29C_BUSHWACKER_RECONCILIATION_LEDGER.json").write_text(
    json.dumps(ledger, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(ledger, indent=2, ensure_ascii=False))
