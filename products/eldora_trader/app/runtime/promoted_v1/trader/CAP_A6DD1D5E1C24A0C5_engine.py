import json
from pathlib import Path
from datetime import datetime, UTC

def build_commands():
    source="reports/P12_REAL_DATA_LOADING_CLOUD_EXPORT/export_package"
    return {
        "rclone_drive": f'rclone copy "{source}" "gdrive:mind-workspace/MIND_TRADER/P12_EXPORT_PACKAGE" --create-empty-src-dirs --progress',
        "supabase_note": "Upload package files to bucket mind-workspace/MIND_TRADER/P12_EXPORT_PACKAGE using existing project credentials.",
        "source_dir": source
    }

def run():
    out=Path("reports/P12.1_CLOUD_EXPORT_COMMAND_PACK")
    out.mkdir(parents=True,exist_ok=True)
    commands=build_commands()
    manifest={
        "STATUS":"P12.1_CLOUD_EXPORT_COMMAND_PACK_IMPLEMENTED",
        "COMMANDS":commands,
        "CLOUD_TARGETS":["Google Drive via rclone","Supabase bucket mind-workspace"],
        "LOCAL_PACKAGE_IS_TEMPORARY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"P12.1_cloud_export_commands.json").write_text(json.dumps(commands,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P12.1_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
