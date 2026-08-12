import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
INPUTS = [
    OUT / "p1505g_mt5_monte_carlo_results.json",
    OUT / "p1505l_remaining_mt5_mc_results.json"
]
REPORT = OUT / "p1505_payoff_metrics_report.json"

all_rows = []
for p in INPUTS:
    if p.exists():
        all_rows += json.loads(p.read_text(encoding="utf-8"))

enriched = []

for r in all_rows:
    pf = float(r.get("profit_factor") or 0)
    dd = float(r.get("max_drawdown_proxy") or 0)
    trades = int(r.get("trades") or 0)
    score = float(r.get("score") or 0)

    # Proxy conservador porque os arquivos atuais não guardam cada trade individual.
    avg_loss = round(max(dd, 0.0001) / max(trades, 1), 8)
    avg_win = round(avg_loss * pf, 8)
    payoff_ratio = round(avg_win / avg_loss, 6) if avg_loss else 0
    expectancy = round(((pf - 1) / max(trades, 1)), 8)

    enriched.append({
        **r,
        "average_win_proxy": avg_win,
        "average_loss_proxy": avg_loss,
        "payoff_ratio_proxy": payoff_ratio,
        "expectancy_per_trade_proxy": expectancy,
        "payoff_metric_mode": "PROXY_FROM_PF_DD_TRADES"
    })

by_asset = {}
for r in enriched:
    a = r.get("asset")
    by_asset.setdefault(a, []).append(r)

asset_summary = {}
for asset, rows in by_asset.items():
    asset_summary[asset] = {
        "edges": len(rows),
        "avg_payoff_ratio_proxy": round(sum(x["payoff_ratio_proxy"] for x in rows) / len(rows), 6),
        "avg_expectancy_per_trade_proxy": round(sum(x["expectancy_per_trade_proxy"] for x in rows) / len(rows), 8),
        "best_payoff_ratio_proxy": max(x["payoff_ratio_proxy"] for x in rows),
        "best_expectancy_per_trade_proxy": max(x["expectancy_per_trade_proxy"] for x in rows)
    }

report = {
    "STATUS": "P1505_PAYOFF_METRICS_PATCH_COMPLETED",
    "EDGES_ANALYZED": len(enriched),
    "ASSET_SUMMARY": asset_summary,
    "NOTE": "Proxy calculado a partir de profit_factor, drawdown e trades. Para payoff real, o backtest precisa salvar lista de trades individuais.",
    "NEXT": "PATCH_BACKTEST_ENGINE_TO_SAVE_TRADE_LEVEL_PAYOFF",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1505_edges_with_payoff_metrics.json").write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
