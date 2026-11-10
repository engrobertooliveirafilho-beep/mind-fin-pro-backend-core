"""ET665 R246: fail-closed PAPER-only floating equity and ensemble roster diagnostics.

This module does not recover strategy rules, calibrate costs, or certify performance.
Bars must be chronologically ordered, aligned with entries/exits, and use BID OHLC.
"""
from collections import defaultdict
from datetime import datetime
from math import isfinite

def _time(x):
    return datetime.fromisoformat(str(x).replace("Z", "+00:00"))

def _number(x, name):
    if x is None:
        raise ValueError("Missing " + name)
    v = float(x)
    if not isfinite(v):
        raise ValueError("Nonfinite " + name)
    return v

def floating_equity(bars, positions, initial_equity, point_size, contract_size):
    """Mark every active position to conservative liquidation prices at each bar.

    positions: entry_time, exit_time, side, lots, entry_fill, exit_fill,
    entry_cost_cash, exit_cost_cash, fx_rate, and PAPER safety fields.
    Costs must be precomputed explicitly in account currency. No fabricated fills.
    Mark uses bar low for BUY and high+spread for SELL to expose adverse
    intrabar equity. Exit cash uses the supplied executed exit_fill.
    """
    cash = _number(initial_equity, "initial_equity")
    point = _number(point_size, "point_size")
    contract = _number(contract_size, "contract_size")
    if cash <= 0 or point <= 0 or contract <= 0 or not bars:
        raise ValueError("Invalid equity/contract/bars")
    ordered = []
    prev = None
    for bar in bars:
        t = _time(bar.get("timestamp", bar.get("time")))
        if prev is not None and t <= prev:
            raise ValueError("Bars not strictly chronological")
        prev = t
        lo, hi = _number(bar.get("low"), "low"), _number(bar.get("high"), "high")
        spread = _number(bar.get("spread"), "spread")
        if lo > hi or spread < 0:
            raise ValueError("Invalid OHLC/spread")
        ordered.append((t, lo, hi, spread))
    timeline = {t for t, *_ in ordered}
    starts, ends = defaultdict(list), defaultdict(list)
    for i, p in enumerate(positions):
        if (p.get("mode") != "PAPER_ONLY" or p.get("real_orders") != "FORBIDDEN"
            or p.get("ftmo_real") != "FORBIDDEN" or p.get("real_execution_allowed") is not False):
            raise ValueError("PAPER safety contract failed")
        en, ex = _time(p["entry_time"]), _time(p["exit_time"])
        if en not in timeline or ex not in timeline or ex <= en:
            raise ValueError("Position timestamps must align with canonical bars")
        side = p.get("side")
        if side not in ("BUY", "SELL"):
            raise ValueError("Invalid side")
        lots = _number(p.get("lots"), "lots")
        fx = _number(p.get("fx_rate"), "fx_rate")
        entry = _number(p.get("entry_fill"), "entry_fill")
        exit_fill = _number(p.get("exit_fill"), "exit_fill")
        ec = _number(p.get("entry_cost_cash"), "entry_cost_cash")
        xc = _number(p.get("exit_cost_cash"), "exit_cost_cash")
        if lots <= 0 or fx <= 0 or ec < 0 or xc < 0:
            raise ValueError("Invalid lots/FX/cost")
        starts[en].append((i, p))
        ends[ex].append((i, p))
    active = {}
    peak = cash
    maximum_dd = 0.0
    curve = []
    for t, low, high, spread in ordered:
        for i, p in ends[t]:
            if i not in active:
                raise ValueError("Exit without active position")
            sign = 1 if p["side"] == "BUY" else -1
            cash += sign * (float(p["exit_fill"]) - float(p["entry_fill"])) * float(p["lots"]) * contract * float(p["fx_rate"])
            cash -= float(p["exit_cost_cash"])
            del active[i]
        for i, p in starts[t]:
            cash -= float(p["entry_cost_cash"])
            active[i] = p
        floating = 0.0
        for p in active.values():
            mark = low if p["side"] == "BUY" else high + spread * point
            sign = 1 if p["side"] == "BUY" else -1
            floating += sign * (mark - float(p["entry_fill"])) * float(p["lots"]) * contract * float(p["fx_rate"])
            floating -= float(p["exit_cost_cash"])
        equity = cash + floating
        peak = max(peak, equity)
        maximum_dd = max(maximum_dd, (peak - equity) / peak)
        curve.append({"timestamp": t.isoformat(), "cash": cash, "floating_pnl": floating,
                      "equity": equity, "active_positions": len(active),
                      "drawdown_pct": maximum_dd * 100})
    if active:
        raise ValueError("Unclosed positions")
    return {"equity_end": cash, "max_intrabar_adverse_drawdown_pct": maximum_dd * 100,
            "curve": curve, "status": "PAPER_ONLY_UNCERTIFIED"}

def ensemble_feasibility(members, quorum=3, max_family_concentration=0.4):
    """Audit roster diversity; never create or promote fabricated strategies."""
    if quorum < 1 or not 0 < max_family_concentration <= 1:
        raise ValueError("Invalid policy")
    groups = defaultdict(list)
    seen = set()
    for m in members:
        if m.get("status") != "ENSEMBLE_MEMBER":
            continue
        eid = str(m.get("edge_id", ""))
        if not eid or eid in seen:
            raise ValueError("Duplicate or missing edge ID")
        seen.add(eid)
        if not all(m.get(k) for k in ("session", "regime", "timeframe", "family")):
            raise ValueError("Missing context/family")
        w = _number(m.get("ensemble_weight"), "ensemble_weight")
        if w <= 0:
            raise ValueError("Nonpositive weight")
        groups[(m["session"], m["regime"], m["timeframe"])].append(m)
    result = []
    for context, rows in sorted(groups.items()):
        total = sum(float(m["ensemble_weight"]) for m in rows)
        family = defaultdict(float)
        for m in rows:
            family[m["family"]] += float(m["ensemble_weight"])
        concentration = max(family.values()) / total
        feasible = len(rows) >= quorum and concentration <= max_family_concentration
        result.append({"context": context, "members": len(rows),
                       "distinct_families": len(family), "family_concentration": concentration,
                       "structurally_feasible": feasible})
    return {"contexts": result, "feasible_contexts": sum(x["structurally_feasible"] for x in result),
            "certified": False, "runtime_allowed": False}
