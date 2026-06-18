from __future__ import annotations
import json,time,hashlib
from pathlib import Path

class EvidenceRegistry:
    def __init__(self):
        self.root=Path("_evidence/P4.47D_EVIDENCE")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"evidence.jsonl"

    def register(self,experiment_id:str,evidence_type:str,payload:dict):
        evidence_id=hashlib.sha256(
            f"{experiment_id}|{time.time()}".encode()
        ).hexdigest()[:16]

        record={
            "evidence_id":evidence_id,
            "experiment_id":experiment_id,
            "timestamp":time.time(),
            "evidence_type":evidence_type,
            "payload":payload
        }

        with self.file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False)+"\n")

        return record

    def count(self):
        if not self.file.exists():
            return 0

        return len(
            self.file.read_text(
                encoding="utf-8"
            ).splitlines()
        )
