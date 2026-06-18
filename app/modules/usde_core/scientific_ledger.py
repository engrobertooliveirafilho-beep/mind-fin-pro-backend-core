from __future__ import annotations
import json,time
from pathlib import Path

class ScientificLedger:
    def __init__(self):
        self.root=Path("_evidence/P4.47B_LEDGER")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"scientific_ledger.jsonl"

    def append(self,event_type:str,payload:dict):
        row={
            "timestamp":time.time(),
            "event_type":event_type,
            "payload":payload
        }

        with self.file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")

        return row

    def count(self):
        if not self.file.exists():
            return 0

        return len(
            self.file.read_text(
                encoding="utf-8"
            ).splitlines()
        )
