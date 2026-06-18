from __future__ import annotations
import json, hashlib, time
from pathlib import Path

class ScientificMemory:
    def __init__(self, root:str="_evidence/P4.46X_USDE_CORE/scientific_memory"):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)
        self.memory_file=self.root/"memory.jsonl"

    def _hash(self,payload:dict)->str:
        raw=json.dumps(payload,ensure_ascii=False,sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def store(self,category:str,payload:dict)->dict:
        record={
            "timestamp":time.time(),
            "category":category,
            "payload":payload
        }
        record["memory_id"]=self._hash(record)

        with self.memory_file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False)+"\n")

        return record

    def load(self)->list[dict]:
        if not self.memory_file.exists():
            return []

        return [
            json.loads(x)
            for x in self.memory_file.read_text(
                encoding="utf-8"
            ).splitlines()
            if x.strip()
        ]

    def query(self,category:str)->list[dict]:
        return [
            x
            for x in self.load()
            if x["category"]==category
        ]
