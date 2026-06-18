
import os
import json
import urllib.request
from p56g4_strict_entity_validator import validate_pedigree_edge

ALLOWED_SOURCE_TYPES = {
    "ABBI_PROFILE",
    "PBR_PROFILE",
    "SALE_CATALOG",
    "SEMEN_CATALOG",
    "EMBRYO_CATALOG",
    "BREEDER_REGISTRY"
}

class StructuredPedigreeSourceConnector:
    def __init__(self, url=None, key=None):
        self.url = (url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.key = key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        r = urllib.request.Request(
            self.url + path,
            data=data,
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=representation"
            },
            method=method
        )
        with urllib.request.urlopen(r, timeout=30) as x:
            body = x.read().decode("utf-8")
            return json.loads(body) if body else []

    def validate_record(self, record):
        required = ["animal", "source_url", "source_type", "confidence"]
        missing = [k for k in required if not record.get(k)]

        if missing:
            return {"status": "REJECT", "reasons": ["MISSING_FIELDS"], "missing": missing}

        if record["source_type"] not in ALLOWED_SOURCE_TYPES:
            return {"status": "REJECT", "reasons": ["INVALID_SOURCE_TYPE"]}

        if float(record["confidence"]) < 60:
            return {"status": "REJECT", "reasons": ["CONFIDENCE_LT_60"]}

        if not record.get("sire") and not record.get("dam"):
            return {"status": "REJECT", "reasons": ["NO_PARENT_FIELDS"]}

        checks = []

        if record.get("sire"):
            checks.append(validate_pedigree_edge(
                record["sire"],
                record["animal"],
                "sire",
                record["confidence"],
                record["source_url"]
            ))

        if record.get("dam"):
            checks.append(validate_pedigree_edge(
                record["dam"],
                record["animal"],
                "dam",
                record["confidence"],
                record["source_url"]
            ))

        rejected = [c for c in checks if c["status"] != "PASS"]

        if rejected:
            return {"status": "REJECT", "reasons": ["VALIDATOR_REJECTED"], "checks": checks}

        return {"status": "PASS", "checks": checks}

    def run_batch(self, records):
        accepted = []
        rejected = []

        for record in records:
            validation = self.validate_record(record)
            item = {"record": record, "validation": validation}

            if validation["status"] == "PASS":
                accepted.append(item)
            else:
                rejected.append(item)

        return {
            "status": "P5.6G15_STRUCTURED_CONNECTOR_DONE",
            "accepted": len(accepted),
            "rejected": len(rejected),
            "accepted_items": accepted,
            "rejected_items": rejected
        }
