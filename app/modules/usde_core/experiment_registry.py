from __future__ import annotations
import json,time,hashlib
from pathlib import Path

class ExperimentRegistry:
    def __init__(self):
        self.root=Path("_evidence/P4.47C_EXPERIMENTS")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"experiments.jsonl"

    def register(self,name:str,parameters:dict):
        eid=hashlib.sha256(
            f"{name}|{time.time()}".encode()
        ).hexdigest()[:16]

        record={
            "experiment_id":eid,
            "timestamp":time.time(),
            "name":name,
            "parameters":parameters
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
