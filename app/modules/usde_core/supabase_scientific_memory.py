from __future__ import annotations
import json,time
from pathlib import Path

class SupabaseScientificMemory:
    def __init__(self):
        self.root=Path("_evidence/P4.47O_SUPABASE_MEMORY")
        self.root.mkdir(parents=True,exist_ok=True)
        self.file=self.root/"supabase_scientific_memory_mock.jsonl"

    def upsert(self,table:str,payload:dict):
        record={
            "table":table,
            "timestamp":time.time(),
            "payload":payload
        }

        with self.file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False)+"\n")

        return {
            "status":"UPSERTED",
            "table":table
        }

    def count(self):
        if not self.file.exists():
            return 0
        return len(self.file.read_text(encoding="utf-8").splitlines())
