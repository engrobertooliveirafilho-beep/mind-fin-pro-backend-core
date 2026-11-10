"""ET665.R278 offline chronological evaluation of existing trade records.
NOT a replacement for causal point-in-time walk-forward. No runtime promotion.
"""
import csv, hashlib, json, math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def evaluate_trade_file(source, destination, windows=5):
    source = Path(source)
    rows = defaultdict(list)
    invalid = []
    with source.open(encoding="utf-8-sig", newline="") as handle:
        for number, record in enumerate(csv.DictReader(handle), 2):
            try:
                assert record["mode"] == "PAPER_ONLY"
                assert record["real_orders"] == "FORBIDDEN"
                assert record["ftmo_real"] == "FORBIDDEN"
                assert record["real_execution_allowed"].lower() == "false"
                entry = datetime.fromisoformat(record["entry_time"])
                exit_time = datetime.fromisoformat(record["exit_time"])
                pnl = float(record["pnl_r"])
                assert exit_time >= entry and math.isfinite(pnl)
                rows[record["edge_id"]].append((entry, pnl))
            except (AssertionError, KeyError, ValueError) as error:
                invalid.append({"line": number, "error": str(error)})
    edges = []
    for edge_id, trades in sorted(rows.items()):
        trades.sort()
        folds = []
        for i in range(windows):
            part = trades[len(trades)*i//windows:len(trades)*(i+1)//windows]
            if not part:
                continue
            profits = sum(p for _,p in part if p>0)
            losses = -sum(p for _,p in part if p<0)
            equity = peak = drawdown = 0.0
            for _,p in part:
                equity += p
                peak = max(peak,equity)
                drawdown = max(drawdown,peak-equity)
            folds.append({"fold":i+1,"count":len(part),"start":part[0][0].isoformat(),
                          "end":part[-1][0].isoformat(),
                          "profit_factor":profits/losses if losses else None,
                          "expectancy_r":sum(p for _,p in part)/len(part),"max_dd_r":drawdown})
        edges.append({"edge_id":edge_id,"trades":len(trades),"folds":folds,
                      "status":"QUARANTINE","runtime_promotion_allowed":False})
    result = {"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "edge_count":len(edges),"trade_count":sum(map(len,rows.values())),
              "invalid_rows":invalid,"edges":edges,"runtime_promotion_allowed":False,
              "method":"chronological nonoverlapping folds; no causal signal replay",
              "limitations":["canonical OHLC equivalence unverified","signal lookahead unverified"]}
    Path(destination).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
