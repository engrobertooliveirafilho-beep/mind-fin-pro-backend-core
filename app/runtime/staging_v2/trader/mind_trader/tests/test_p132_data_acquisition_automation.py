from pathlib import Path
from app.p13_data_acquisition_automation.engine import build_acquisition_plan, run, WATCH_DIRS

def test_p132_acquisition_plan_exists():
    p=build_acquisition_plan()
    assert len(p)>0
    assert all(x["auto_ingest_enabled"] is True for x in p)

def test_p132_watch_dirs_created():
    run()
    for d in WATCH_DIRS:
        assert Path(d).exists()

def test_p132_blocks_live():
    m=run()
    assert m["LIVE"]=="FORBIDDEN"
    assert m["REAL_BROKER"]=="DISABLED"
    assert m["EXPORT_READY"] is True
