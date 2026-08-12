from pathlib import Path
import csv, json
from datetime import datetime, timezone

STATUS = "P14.15_PROFIT_STRATEGY_FACTORY_METRICS_TRACKER_IMPLEMENTED"

ROOT = Path(".")
METRICS_DIR = ROOT / "data" / "incoming" / "profit_backtest_results"
REPORT_DIR = ROOT / "reports" / "P14.15_PROFIT_STRATEGY_FACTORY_METRICS"
CSV_FILE = METRICS_DIR / "backtest_results.csv"

REQUIRED_COLUMNS = {
    "strategy_id",
    "file",
    "net_profit",
    "profit_factor",
    "drawdown",
    "win_rate",
    "trades",
}

def parse_float(v):
    if v is None or str(v).strip() == "":
        return 0.0
    return float(str(v).replace(",", ".").replace("R$", "").strip())

def parse_int(v):
    if v is None or str(v).strip() == "":
        return 0
    return int(float(str(v).replace(",", ".").strip()))

def inspect_results(path=CSV_FILE):
    if not path.exists():
        return {
            "valid": False,
            "reason": "CSV_NOT_FOUND",
            "rows": 0,
            "ranked": []
        }

    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return {
            "valid": False,
            "reason": "CSV_EMPTY",
            "rows": 0,
            "ranked": []
        }

    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing:
        return {
            "valid": False,
            "reason": "MISSING_COLUMNS",
            "missing": sorted(missing),
            "rows": len(rows),
            "ranked": []
        }

    ranked = []
    for r in rows:
        net_profit = parse_float(r["net_profit"])
        profit_factor = parse_float(r["profit_factor"])
        drawdown = abs(parse_float(r["drawdown"]))
        win_rate = parse_float(r["win_rate"])
        trades = parse_int(r["trades"])

        score = (
            net_profit
            + profit_factor * 1000
            + win_rate * 10
            - drawdown * 2
            + min(trades, 500) * 2
        )

        ranked.append({
            "strategy_id": r["strategy_id"],
            "file": r["file"],
            "net_profit": net_profit,
            "profit_factor": profit_factor,
            "drawdown": drawdown,
            "win_rate": win_rate,
            "trades": trades,
            "score": round(score, 4)
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return {
        "valid": True,
        "reason": "OK",
        "rows": len(rows),
        "ranked": ranked,
        "best": ranked[0] if ranked else None
    }

def run():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    result = inspect_results()

    manifest = {
        "STATUS": STATUS,
        "METRICS_CSV": str(CSV_FILE),
        "REQUIRED_COLUMNS": sorted(REQUIRED_COLUMNS),
        "RESULT": result,
        "RANKING_POLICY": "net_profit + profit_factor*1000 + win_rate*10 - drawdown*2 + capped_trades*2",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.15_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    template = "strategy_id,file,net_profit,profit_factor,drawdown,win_rate,trades\n"
    template += "p1414_inline_media_f3_s21,p1414_inline_media_f3_s21.nts,0,0,0,0,0\n"
    template += "p1414_inline_media_f8_s34,p1414_inline_media_f8_s34.nts,0,0,0,0,0\n"
    template += "p1414_inline_media_f21_s55,p1414_inline_media_f21_s55.nts,0,0,0,0,0\n"

    (REPORT_DIR / "backtest_results_template.csv").write_text(template, encoding="utf-8")

    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
