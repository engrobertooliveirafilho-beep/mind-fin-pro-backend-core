from __future__ import annotations
import json,time,hashlib
from pathlib import Path

class ExperimentQueue:
    def __init__(self):
        self.root=Path("_evidence/P4.47Q_EXPERIMENT_QUEUE")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"queue.jsonl"

    def enqueue(self,experiment:dict):
        job_id=hashlib.sha256(
            f"{experiment}|{time.time()}".encode()
        ).hexdigest()[:16]

        record={
            "job_id":job_id,
            "timestamp":time.time(),
            "status":"QUEUED",
            "experiment":experiment
        }

        with self.file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False)+"\n")

        return record

    def count(self):
        if not self.file.exists():
            return 0
        return len(self.file.read_text(encoding="utf-8").splitlines())
