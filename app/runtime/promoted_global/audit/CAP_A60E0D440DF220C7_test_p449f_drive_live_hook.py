from pathlib import Path
from app.modules.usde_core.drive_live_hook import USDEDriveLiveHook

def test_drive_live_hook():
    p=Path("_evidence/test_drive_live_hook.txt")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text("ok",encoding="utf-8")

    r=USDEDriveLiveHook().observe_file(str(p))

    assert r["ingestion"]["exists"] is True
    assert "hypothesis" in r["observation"]
    assert "experiment" in r["observation"]
    assert "evidence" in r["observation"]
    assert "decision" in r["observation"]
