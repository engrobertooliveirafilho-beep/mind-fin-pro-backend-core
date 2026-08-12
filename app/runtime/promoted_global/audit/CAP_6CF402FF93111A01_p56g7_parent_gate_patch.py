from pathlib import Path
from datetime import datetime, timezone

target = Path("app/mind/p5_5v_pedigree_extractor/extractor.py")
text = target.read_text(encoding="utf-8")

backup = target.with_suffix(".py.bak_p56g7_parent_gate_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"))
backup.write_text(text, encoding="utf-8")

old = '''        parent=self.find_or_create_animal(parent_name,confidence)
        child=self.find_or_create_animal(child_name,confidence)
        payload={"parent_id":parent["id"],"child_id":child["id"],"relation":relation,"generation_distance":1,"evidence_source_id":source_id,"confidence_score":confidence,"validation_status":"provisional"}
'''

new = '''        pk=key(parent_name)
        pq=urllib.parse.quote(pk)
        parent_rows=self.req("GET",f"/rest/v1/p55a_animals?identity_key=eq.{pq}&select=id,official_name,identity_key,confidence_score,validation_status")

        if not parent_rows:
            try:
                self.req("POST","/rest/v1/p55a_audit_logs",{
                    "event_type":"P5.6G7_PARENT_NOT_PREEXISTING_REJECTED",
                    "raw_payload":{"parent_name":parent_name,"child_name":child_name,"relation":relation,"source_id":source_id},
                    "confidence_score":confidence,
                    "validation_status":"rejected"
                })
            except Exception:
                pass
            return None

        parent=parent_rows[0]

        if str(parent.get("validation_status")) in {"weak","quarantined"} or float(parent.get("confidence_score") or 0) <= 40:
            try:
                self.req("POST","/rest/v1/p55a_audit_logs",{
                    "event_type":"P5.6G7_PARENT_QUALITY_REJECTED",
                    "raw_payload":{"parent":parent,"child_name":child_name,"relation":relation,"source_id":source_id},
                    "confidence_score":confidence,
                    "validation_status":"rejected"
                })
            except Exception:
                pass
            return None

        child=self.find_or_create_animal(child_name,confidence)
        payload={"parent_id":parent["id"],"child_id":child["id"],"relation":relation,"generation_distance":1,"evidence_source_id":source_id,"confidence_score":confidence,"validation_status":"provisional"}
'''

if old not in text:
    raise RuntimeError("target block not found")

text = text.replace(old,new)
target.write_text(text,encoding="utf-8")

print("PATCHED=",target)
print("BACKUP=",backup)
print("PARENT_GATE_OK=", "P5.6G7_PARENT_QUALITY_REJECTED" in text)
