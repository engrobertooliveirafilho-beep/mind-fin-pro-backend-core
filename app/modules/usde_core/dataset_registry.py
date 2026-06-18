from __future__ import annotations
import json,time,hashlib
from pathlib import Path

class DatasetRegistry:
    def __init__(self):
        self.root=Path("_evidence/P4.47P_DATASETS")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"datasets.jsonl"

    def register(self,path:str,metadata:dict|None=None):
        dataset_id=hashlib.sha256(
            f"{path}|{time.time()}".encode()
        ).hexdigest()[:16]

        record={
            "dataset_id":dataset_id,
            "timestamp":time.time(),
            "path":path,
            "metadata":metadata or {}
        }

        with self.file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False)+"\n")

        return record

    def count(self):
        if not self.file.exists():
            return 0
        return len(self.file.read_text(encoding="utf-8").splitlines())
