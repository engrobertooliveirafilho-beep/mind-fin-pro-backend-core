from __future__ import annotations
import json,time,hashlib
from pathlib import Path

class HypothesisRegistry:
    def __init__(self):
        self.root=Path("_evidence/P4.47E_HYPOTHESES")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"hypotheses.jsonl"

    def register(self,name:str,statement:str):
        hypothesis_id=hashlib.sha256(
            f"{name}|{statement}|{time.time()}".encode()
        ).hexdigest()[:16]

        record={
            "hypothesis_id":hypothesis_id,
            "timestamp":time.time(),
            "name":name,
            "statement":statement,
            "status":"REGISTERED"
        }

        with self.file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False)+"`n")

        return record

    def count(self):
        if not self.file.exists():
            return 0

        return len(
            self.file.read_text(
                encoding="utf-8"
            ).splitlines()
        )
