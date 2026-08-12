from pathlib import Path
from datetime import datetime, timezone

target = Path("app/mind/p5_5v_pedigree_extractor/extractor.py")
text = target.read_text(encoding="utf-8")

backup = target.with_suffix(
    ".py.bak_p56g5_safe_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
)
backup.write_text(text, encoding="utf-8")

# 1. Add clean import after current import line
if "from p56g4_strict_entity_validator import validate_pedigree_edge" not in text:
    text = text.replace(
        "import os, json, re, hashlib, urllib.request, urllib.parse\n",
        "import os, json, re, hashlib, urllib.request, urllib.parse\nfrom p56g4_strict_entity_validator import validate_pedigree_edge\n"
    )

old = '''    def create_edge(self, parent_name, child_name, relation, source_id):
        parent=self.find_or_create_animal(parent_name,35)
        child=self.find_or_create_animal(child_name,45)
        payload={"parent_id":parent["id"],"child_id":child["id"],"relation":relation,"generation_distance":1,"evidence_source_id":source_id,"confidence_score":35,"validation_status":"weak"}
        try:
            return self.req("POST","/rest/v1/p55a_pedigree_edges?on_conflict=parent_id,child_id,relation",payload)[0]
        except Exception:
            return None
'''

new = '''    def create_edge(self, parent_name, child_name, relation, source_id):
        confidence = 60 if source_id else 35
        validation = validate_pedigree_edge(parent_name, child_name, relation, confidence, source_id)

        if validation["status"] != "PASS":
            try:
                self.req("POST","/rest/v1/p55a_audit_logs",{
                    "event_type":"P5.6G5_PEDIGREE_EDGE_REJECTED",
                    "raw_payload":validation,
                    "confidence_score":confidence,
                    "validation_status":"rejected"
                })
            except Exception:
                pass
            return None

        parent=self.find_or_create_animal(parent_name,confidence)
        child=self.find_or_create_animal(child_name,confidence)
        payload={"parent_id":parent["id"],"child_id":child["id"],"relation":relation,"generation_distance":1,"evidence_source_id":source_id,"confidence_score":confidence,"validation_status":"provisional"}
        try:
            return self.req("POST","/rest/v1/p55a_pedigree_edges?on_conflict=parent_id,child_id,relation",payload)[0]
        except Exception:
            return None
'''

if old not in text:
    raise RuntimeError("create_edge block not found; no patch applied")

text = text.replace(old, new)

target.write_text(text, encoding="utf-8")

print("PATCHED=", target)
print("BACKUP=", backup)
print("IMPORT_OK=", "from p56g4_strict_entity_validator import validate_pedigree_edge" in text)
print("GUARD_OK=", "P5.6G5_PEDIGREE_EDGE_REJECTED" in text)
