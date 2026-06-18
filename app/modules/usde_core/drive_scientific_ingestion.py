from __future__ import annotations
from pathlib import Path

class DriveScientificIngestion:
    def ingest(self,path:str):
        p=Path(path)

        return {
            "exists":p.exists(),
            "name":p.name,
            "suffix":p.suffix,
            "size":p.stat().st_size if p.exists() else 0
        }
