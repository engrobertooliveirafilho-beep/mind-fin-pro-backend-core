from __future__ import annotations

from app.modules.usde_core.drive_scientific_ingestion import DriveScientificIngestion
from app.modules.usde_core.live_bridge import USDELiveBridge

class USDEDriveLiveHook:
    def observe_file(self,path:str):
        ingestion = DriveScientificIngestion().ingest(path)

        observation = USDELiveBridge().observe(
            "drive",
            {
                "type": "drive_file_event",
                "file": ingestion.get("name"),
                "exists": ingestion.get("exists"),
                "size": ingestion.get("size")
            }
        )

        return {
            "ingestion": ingestion,
            "observation": observation
        }
