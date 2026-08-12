from app.p12_cloud_export_command_pack.engine import build_commands, run

def test_p121_builds_rclone_command():
    c=build_commands()
    assert "rclone copy" in c["rclone_drive"]
    assert "gdrive:mind-workspace/MIND_TRADER/P12_EXPORT_PACKAGE" in c["rclone_drive"]

def test_p121_manifest_blocks_live():
    m=run()
    assert m["STATUS"]=="P12.1_CLOUD_EXPORT_COMMAND_PACK_IMPLEMENTED"
    assert m["LIVE"]=="FORBIDDEN"
    assert m["REAL_BROKER"]=="DISABLED"

def test_p121_export_ready():
    m=run()
    assert m["EXPORT_READY"] is True
    assert m["LOCAL_PACKAGE_IS_TEMPORARY"] is True
