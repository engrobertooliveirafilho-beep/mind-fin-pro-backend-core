from app.p13_cloud_sync_automation.engine import build_sync_commands, run

def test_p135_builds_rclone_commands():
    c=build_sync_commands()
    assert "rclone copy" in c["reports_to_drive"]
    assert "rclone copy" in c["data_to_drive"]

def test_p135_manifest_blocks_live():
    m=run()
    assert m["STATUS"]=="P13.5_CLOUD_SYNC_AUTOMATION_IMPLEMENTED"
    assert m["LIVE"]=="FORBIDDEN"
    assert m["REAL_BROKER"]=="DISABLED"

def test_p135_export_ready():
    m=run()
    assert m["EXPORT_READY"] is True
    assert m["LOCAL_DATA_TEMPORARY"] is True
