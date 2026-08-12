import json
from pathlib import Path

def test_p491f2_drive_scan_monitor():
    report = json.loads(Path("runtime/drive_absorption/monitor/drive_scan_monitor_report.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.91F2 COMPLETE"
    assert report["monitor"] == "DRIVE_SCAN_MONITOR"
    assert report["mode"] == "PRINT_SCAN_PROGRESS"
    assert report["delete"] == "FORBIDDEN"
    assert report["move_original"] == "FORBIDDEN"
    assert "files_total" in report
    assert "zip_files" in report
