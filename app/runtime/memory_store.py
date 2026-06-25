import json
import os
from pathlib import Path
from threading import Lock

class SimpleMemoryStore:
    def __init__(self):
        self.lock = Lock()
        self.file = Path("memory_store.json")
        if not self.file.exists():
            self.file.write_text("{}", encoding="utf-8")

    def _load(self):
        try:
            return json.loads(self.file.read_text(encoding="utf-8"))
        except:
            return {}

    def _save(self, data):
        self.file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def save(self, sender_id, text):
        with self.lock:
            data = self._load()
            if sender_id not in data:
                data[sender_id] = []
            data[sender_id].append(text)
            data[sender_id] = data[sender_id][-20:]
            self._save(data)

    def recall(self, sender_id, limit=8):
        with self.lock:
            data = self._load()
            history = data.get(sender_id, [])
            return history[-limit:] if history else []
