from __future__ import annotations
import json,time,hashlib
from pathlib import Path

class DecisionRegistry:
    def __init__(self):
        self.root=Path("_evidence/P4.47F_DECISIONS")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"decisions.jsonl"

    def register(self,hypothesis_id:str,decision:str,evidence:dict):
        decision_id=hashlib.sha256(
            f"{hypothesis_id}|{decision}|{time.time()}".encode()
        ).hexdigest()[:16]

        record={
            "decision_id":decision_id,
            "hypothesis_id":hypothesis_id,
            "timestamp":time.time(),
            "decision":decision,
            "evidence":evidence
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
