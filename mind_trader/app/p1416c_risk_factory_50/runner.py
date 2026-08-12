from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.16C_RISK_FACTORY_50_IMPLEMENTED"

ROOT = Path(".")
EXPORT_DIR = ROOT / "profit_import_package"
REPORT_DIR = ROOT / "reports" / "P14.16C_RISK_FACTORY_50"

FAST = [3, 5, 8, 9, 13]
SLOW = [21, 34, 55, 89, 144]
TREND = [100, 200]

def build_code(fast, slow, trend):
    return f"""begin
  if (Media({fast}, Close) > Media({slow}, Close)) and (Close > Media({trend}, Close)) then
    BuyAtMarket;

  if (Media({fast}, Close) < Media({slow}, Close)) and (Close < Media({trend}, Close)) then
    SellShortAtMarket;
end;
"""

def run():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for fast in FAST:
        for slow in SLOW:
            for trend in TREND:
                if fast >= slow:
                    continue

                sid = f"p1416c_risk_f{fast}_s{slow}_t{trend}"
                file = f"{sid}.nts"
                path = EXPORT_DIR / file
                path.write_text(build_code(fast, slow, trend), encoding="utf-8")

                generated.append({
                    "strategy_id": sid,
                    "file": file,
                    "fast": fast,
                    "slow": slow,
                    "trend": trend
                })

    manifest = {
        "STATUS": STATUS,
        "COUNT": len(generated),
        "GENERATED": generated,
        "SYNTAX_POLICY": "Inline only. Trend filter only. No var/input/Float/MediaExp/indexing.",
        "GOAL": "Reduce drawdown before adding stop/take syntax.",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.16C_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    csv = "strategy_id,file,net_profit,profit_factor,drawdown,win_rate,trades\n"
    for g in generated:
        csv += f'{g["strategy_id"]},{g["file"]},0,0,0,0,0\n'

    (REPORT_DIR / "backtest_results_template.csv").write_text(csv, encoding="utf-8")
    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
