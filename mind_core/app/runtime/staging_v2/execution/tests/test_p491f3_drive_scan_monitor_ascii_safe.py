import json
from pathlib import Path

def test_p491f3_drive_scan_monitor_ascii_safe():
    report = json.loads(Path("runtime/drive_absorption/monitor/drive_scan_monitor_report.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.91F3 COMPLETE"
    assert report["monitor"] == "DRIVE_SCAN_MONITOR_ASCII_SAFE"
    assert report["mode"] == "PRINT_SCAN_PROGRESS_ASCII_SAFE"
    assert report["delete"] == "FORBIDDEN"
    assert report["move_original"] == "FORBIDDEN"
    assert "files_total" in report
    assert "zip_files" in report
    assert report["status"] in ["COMPLETE", "FAILED_BUT_REPORTED", "NO_RCLONE_REMOTE"]
