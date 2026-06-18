from __future__ import annotations
import json, time, hashlib
from pathlib import Path

class HypothesisLedger:
    def __init__(self, root: str = "_evidence/P4.46X_USDE_CORE/ledger"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.file = self.root / "hypothesis_ledger.jsonl"

    def _hash(self, payload: dict) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def append(self, hypothesis: str, dataset_ref: str, decision: dict, params: dict | None = None) -> dict:
        record = {
            "ts": time.time(),
            "hypothesis": hypothesis,
            "dataset_ref": dataset_ref,
            "params": params or {},
            "decision": decision,
        }
        record["hash"] = self._hash(record)
        with self.file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def all(self) -> list[dict]:
        if not self.file.exists():
            return []
        return [json.loads(line) for line in self.file.read_text(encoding="utf-8").splitlines() if line.strip()]
