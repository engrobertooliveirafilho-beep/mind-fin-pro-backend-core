from pathlib import Path
from app.modules.usde_core.drive_scientific_ingestion import DriveScientificIngestion

def test_drive_ingestion():
    p=Path("_evidence/test_drive_ingestion.txt")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text("ok",encoding="utf-8")

    r=DriveScientificIngestion().ingest(str(p))

    assert r["exists"] is True
    assert r["size"] > 0
