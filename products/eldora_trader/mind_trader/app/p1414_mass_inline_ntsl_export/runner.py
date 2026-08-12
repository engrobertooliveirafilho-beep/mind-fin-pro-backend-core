from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.14_MASS_INLINE_NTSL_EXPORT_IMPLEMENTED"

ROOT = Path(".")
EXPORT_DIR = ROOT / "profit_import_package"
REPORT_DIR = ROOT / "reports" / "P14.14_MASS_INLINE_NTSL_EXPORT"

FAST = [3, 5, 8, 9, 13, 21]
SLOW = [21, 34, 55, 89, 144]

def build_code(fast, slow):
    return f"""begin
  if Media({fast}, Close) > Media({slow}, Close) then
    BuyAtMarket;

  if Media({fast}, Close) < Media({slow}, Close) then
    SellShortAtMarket;
end;
"""

def run():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for fast in FAST:
        for slow in SLOW:
            if fast >= slow:
                continue
            strategy_id = f"p1414_inline_media_f{fast}_s{slow}"
            path = EXPORT_DIR / f"{strategy_id}.nts"
            path.write_text(build_code(fast, slow), encoding="utf-8")
            generated.append({
                "strategy_id": strategy_id,
                "file": path.name,
                "fast": fast,
                "slow": slow
            })

    manifest = {
        "STATUS": STATUS,
        "COUNT": len(generated),
        "GENERATED": generated,
        "SYNTAX_POLICY": "Inline only: no input, no var, no Float, no MediaExp, no series indexing.",
        "COMPAT_BASELINE": "P14.13 inline Media compiled in Profit.",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.14_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    csv = "strategy_id,file,compiled,error\n"
    for g in generated:
        csv += f'{g["strategy_id"]},{g["file"]},false,PENDING_PROFIT_VALIDATION\n'
    (REPORT_DIR / "compile_result_template.csv").write_text(csv, encoding="utf-8")

    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
