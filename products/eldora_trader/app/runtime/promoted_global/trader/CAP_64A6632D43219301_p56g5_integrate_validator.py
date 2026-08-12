from pathlib import Path
from datetime import datetime

target = Path("app/mind/p5_5v_pedigree_extractor/extractor.py")
validator = Path("p56g4_strict_entity_validator.py")

assert target.exists(), f"Target not found: {target}"
assert validator.exists(), f"Validator not found: {validator}"

backup = target.with_suffix(".py.bak_p56g5_" + datetime.utcnow().strftime("%Y%m%d%H%M%S"))
backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

text = target.read_text(encoding="utf-8")

if "p56g4_strict_entity_validator" not in text:
    text = text.replace(
        "import os",
        "import os\nfrom p56g4_strict_entity_validator import validate_pedigree_edge"
    )

insert_guard = """
        validation = validate_pedigree_edge(parent_name, child_name, relation, confidence, source_id)
        if validation["status"] != "PASS":
            self.req("POST", "/rest/v1/p55a_audit_logs", {
                "event_type": "P5.6G5_PEDIGREE_EDGE_REJECTED",
                "payload": validation,
                "confidence_score": confidence,
                "validation_status": "rejected"
            })
            return None
"""

needle = 'return self.req("POST","/rest/v1/p55a_pedigree_edges?on_conflict=parent_id,child_id,relation",payload)[0]'

if needle in text and "P5.6G5_PEDIGREE_EDGE_REJECTED" not in text:
    text = text.replace(needle, insert_guard + "\n        " + needle)

target.write_text(text, encoding="utf-8")

print("PATCHED =", target)
print("BACKUP =", backup)
print("VALIDATOR_INTEGRATED =", "P5.6G5_PEDIGREE_EDGE_REJECTED" in target.read_text(encoding="utf-8"))
