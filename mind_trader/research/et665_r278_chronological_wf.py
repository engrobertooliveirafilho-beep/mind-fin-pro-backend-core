"""ET665.R278 offline chronological evaluation of existing trade records.
NOT a replacement for causal point-in-time walk-forward. No runtime promotion.
"""
import csv, hashlib, json, math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def evaluate_trade_file(source, destination, windows=5):
    if not isinstance(windows, int) or isinstance(windows, bool) or windows < 2 or windows > 100:
        raise ValueError("windows must be an integer from 2 to 100")
    source = Path(source)
    rows = defaultdict(list)
    invalid = []
    seen = set()
    with source.open(encoding="utf-8-sig", newline="") as handle:
        for number, record in enumerate(csv.DictReader(handle), 2):
            try:
                if record["mode"] != "PAPER_ONLY": raise ValueError("MODE_FORBIDDEN")
                if record["real_orders"] != "FORBIDDEN": raise ValueError("REAL_ORDERS_FORBIDDEN")
                if record["ftmo_real"] != "FORBIDDEN": raise ValueError("FTMO_REAL_FORBIDDEN")
                if record["real_execution_allowed"].lower() != "false": raise ValueError("EXECUTION_FLAG_FORBIDDEN")
                entry = datetime.fromisoformat(record["entry_time"])
                exit_time = datetime.fromisoformat(record["exit_time"])
                pnl = float(record["pnl_r"])
                if exit_time < entry or not math.isfinite(pnl): raise ValueError("INVALID_TRADE")
                edge_id = record["edge_id"].strip()
                if not edge_id: raise ValueError("EMPTY_EDGE_ID")
                trade_key = (edge_id, entry, exit_time)
                if trade_key in seen: raise ValueError("DUPLICATE_TRADE")
                seen.add(trade_key)
                rows[edge_id].append((entry, exit_time, pnl))
            except (AssertionError, KeyError, ValueError) as error:
                invalid.append({"line": number, "error": str(error)})
    edges = []
    for edge_id, trades in sorted(rows.items()):
        trades.sort()
        for prev, nxt in zip(trades, trades[1:]):
            if prev[1] > nxt[0]:
                invalid.append({"edge_id":edge_id,"error":"OVERLAPPING_TRADES"})
                break
        folds = []
        for i in range(windows):
            part = trades[len(trades)*i//windows:len(trades)*(i+1)//windows]
            if not part:
                continue
            profits = sum(p for _,_,p in part if p>0)
            losses = -sum(p for _,_,p in part if p<0)
            equity = peak = drawdown = 0.0
            for _,_,p in part:
                equity += p
                peak = max(peak,equity)
                drawdown = max(drawdown,peak-equity)
            folds.append({"fold":i+1,"count":len(part),"start":part[0][0].isoformat(),
                          "end":part[-1][0].isoformat(),
                          "profit_factor":profits/losses if losses else None,
                          "expectancy_r":sum(p for _,_,p in part)/len(part),"max_dd_r":drawdown})
        edges.append({"edge_id":edge_id,"trades":len(trades),"folds":folds,
                      "status":"QUARANTINE","runtime_promotion_allowed":False})
    result = {"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "edge_count":len(edges),"trade_count":sum(map(len,rows.values())),
              "invalid_rows":invalid,"edges":edges,"runtime_promotion_allowed":False,
              "method":"chronological nonoverlapping folds; no causal signal replay",
              "limitations":["canonical OHLC equivalence unverified","signal lookahead unverified"]}
    Path(destination).write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
