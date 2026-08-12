import json
from pathlib import Path
from datetime import datetime, UTC

SYNC_TARGETS={
    "drive":"gdrive:mind-workspace/MIND_TRADER/P13_DATA_FOUNDATION",
    "source_reports":"reports",
    "source_data":"data"
}

def build_sync_commands():
    return {
        "reports_to_drive": f'rclone copy "{SYNC_TARGETS["source_reports"]}" "{SYNC_TARGETS["drive"]}/reports" --create-empty-src-dirs --progress',
        "data_to_drive": f'rclone copy "{SYNC_TARGETS["source_data"]}" "{SYNC_TARGETS["drive"]}/data" --create-empty-src-dirs --progress'
    }

def run():
    out=Path("reports/P13.5_CLOUD_SYNC_AUTOMATION")
    out.mkdir(parents=True,exist_ok=True)
    commands=build_sync_commands()
    manifest={
        "STATUS":"P13.5_CLOUD_SYNC_AUTOMATION_IMPLEMENTED",
        "COMMANDS":commands,
        "CLOUD_TARGET":SYNC_TARGETS["drive"],
        "LOCAL_DATA_TEMPORARY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"P13.5_cloud_sync_commands.json").write_text(json.dumps(commands,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.5_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
