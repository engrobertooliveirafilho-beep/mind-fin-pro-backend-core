from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional


MISSION = "P2377_DE40_REGIME_FIRST_SIGNAL_ROUTER_WITH_XRAY_LIFECYCLE"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]


def sniff(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig", errors="ignore")[:4096]
    first = text.splitlines()[0] if text.splitlines() else ""
    return ";" if first.count(";") > first.count(",") else ","


def load_csv(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sniff(path)))


def write_csv(path: Path, rows: List[Dict]):
    fields = sorted({k for r in rows for k in r.keys()}) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def fnum(v, default=0.0) -> float:
    try:
        if v is None or str(v).strip() == "":
            return default
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return default


def load_candles(path: Path, limit: Optional[int] = None) -> List[Dict]:
    rows = load_csv(path)
    out = []

    for i, r in enumerate(rows):
        out.append({
            "i": i,
            "time": r.get("time", ""),
            "open": fnum(r.get("open")),
            "high": fnum(r.get("high")),
            "low": fnum(r.get("low")),
            "close": fnum(r.get("close")),
            "tick_volume": fnum(r.get("tick_volume", r.get("volume", 0))),
            "spread": fnum(r.get("spread", 0)),
            "real_volume": fnum(r.get("real_volume", 0)),
        })
        if limit and len(out) >= limit:
            break

    return out


def dataset_for_tf(dataset_root: Path, tf: str):
    found = sorted(
        [p for p in dataset_root.rglob("*") if p.is_file() and "DE40" in p.name and f"_{tf}_" in p.name],
        key=lambda x: x.stat().st_size,
        reverse=True,
    )
    return found[0] if found else None


def sma(values: List[float], i: int, p: int):
    if i - p + 1 < 0:
        return None
    return sum(values[i-p+1:i+1]) / p


def atr(candles: List[Dict], i: int, p: int = 14):
    if i - p < 1:
        return None
    vals = []
    for x in range(i-p+1, i+1):
        c = candles[x]
        prev = candles[x-1]
        vals.append(max(
            c["high"] - c["low"],
            abs(c["high"] - prev["close"]),
            abs(c["low"] - prev["close"]),
        ))
    return sum(vals) / len(vals)


def rsi(values: List[float], i: int, p: int = 14):
    if i - p < 1:
        return None
    gains = []
    losses = []
    for x in range(i-p+1, i+1):
        d = values[x] - values[x-1]
        gains.append(max(d, 0))
        losses.append(abs(min(d, 0)))
    ag = sum(gains) / p
    al = sum(losses) / p
    if al == 0:
        return 100.0
    return 100 - (100 / (1 + ag / al))


def session_of(t: str) -> str:
    try:
        h = int(str(t).replace("T", " ").split(" ")[1].split(":")[0])
    except Exception:
        return "UNKNOWN"

    if 7 <= h < 11:
        return "EUROPE_OPEN"
    if 11 <= h < 15:
        return "EUROPE_MID"
    if 15 <= h < 18:
        return "US_OVERLAP"
    return "OFF_SESSION"


def classify_regime(candles: List[Dict], i: int) -> Dict:
    closes = [x["close"] for x in candles]

    c = candles[i]
    a = atr(candles, i, 14)
    ma20 = sma(closes, i, 20)
    ma50 = sma(closes, i, 50)
    ma100 = sma(closes, i, 100)
    rv = rsi(closes, i, 14)

    if not a or not ma20 or not ma50:
        return {
            "regime": "UNKNOWN",
            "trend": "UNKNOWN",
            "volatility": "UNKNOWN",
            "score": 0,
        }

    spread_20_50 = abs(ma20 - ma50) / a
    price_distance_20 = (c["close"] - ma20) / a

    if ma20 > ma50 and spread_20_50 >= 0.45:
        trend = "TREND_UP"
    elif ma20 < ma50 and spread_20_50 >= 0.45:
        trend = "TREND_DOWN"
    else:
        trend = "RANGE"

    candle_range = (c["high"] - c["low"]) / a
    if candle_range >= 1.8:
        volatility = "VOLATILITY_EXPANSION"
    elif candle_range <= 0.65:
        volatility = "VOLATILITY_COMPRESSION"
    else:
        volatility = "NORMAL_VOLATILITY"

    if trend != "RANGE" and volatility == "VOLATILITY_EXPANSION":
        regime = f"{trend}_EXPANSION"
    elif trend != "RANGE":
        regime = trend
    elif volatility == "VOLATILITY_COMPRESSION":
        regime = "RANGE_COMPRESSION"
    else:
        regime = "RANGE"

    score = 0
    if trend != "RANGE":
        score += 35
    if volatility == "VOLATILITY_EXPANSION":
        score += 25
    if abs(price_distance_20) <= 1.2:
        score += 15
    if rv is not None and 35 <= rv <= 65:
        score += 10
    if ma100 and ((ma20 > ma50 > ma100) or (ma20 < ma50 < ma100)):
        score += 15

    return {
        "regime": regime,
        "trend": trend,
        "volatility": volatility,
        "score": min(score, 100),
        "sma20": round(ma20, 6),
        "sma50": round(ma50, 6),
        "sma100": round(ma100, 6) if ma100 else "",
        "atr14": round(a, 6),
        "rsi14": round(rv, 6) if rv is not None else "",
        "distance_to_sma20_atr": round(price_distance_20, 6),
        "spread_sma20_sma50_atr": round(spread_20_50, 6),
    }


def classify_lifecycle(event: Dict, context: Optional[Dict]) -> Dict:
    event_type = event.get("event_type", "")
    direction = event.get("direction", "")
    post_mfe = fnum(context.get("post_mfe_atr")) if context else 0
    post_mae = fnum(context.get("post_mae_atr")) if context else 0
    efficiency = fnum(context.get("post_efficiency")) if context else 0
    follow = context.get("post_followthrough", "") if context else ""

    lifecycle = "UNCLASSIFIED"
    score = 0

    if "SWEEP" in event_type:
        if post_mfe >= 1.0 and efficiency >= 1.2:
            lifecycle = "LIQUIDITY_REVERSAL_ENTRY"
            score = 80
        elif post_mae > post_mfe:
            lifecycle = "FAILED_SWEEP"
            score = 35
        else:
            lifecycle = "LIQUIDITY_TEST"
            score = 55

    elif "DISPLACEMENT" in event_type:
        if follow == "CONTINUATION" and post_mfe >= 1.0:
            lifecycle = "INSTITUTIONAL_ENTRY_CONTINUATION"
            score = 85
        elif post_mae >= post_mfe:
            lifecycle = "EXHAUSTION_OR_FAKE_DISPLACEMENT"
            score = 40
        else:
            lifecycle = "DISPLACEMENT_RETEST_PENDING"
            score = 65

    elif "RANGE_EXPANSION" in event_type:
        if post_mfe >= 1.5:
            lifecycle = "VOLATILITY_EXPANSION_CONTINUATION"
            score = 75
        else:
            lifecycle = "VOLATILITY_SPIKE_UNRESOLVED"
            score = 45

    if direction == "BUY_INFERRED" and "DOWN" in event_type:
        score -= 5
    if direction == "SELL_INFERRED" and "UP" in event_type:
        score -= 5

    return {
        "lifecycle": lifecycle,
        "lifecycle_score": max(0, min(score, 100)),
        "post_mfe_atr": post_mfe,
        "post_mae_atr": post_mae,
        "post_efficiency": efficiency,
    }


def recommended_families(regime: str, lifecycle: str, footprint: str, volatility: str) -> Dict:
    recommended = []
    rejected = []
    reason = []

    if "TREND_UP" in regime or "TREND_DOWN" in regime:
        recommended += ["TREND_FOLLOWING", "PULLBACK"]
        rejected += ["PURE_COUNTER_TREND"]
        reason.append("trend regime favors continuation or pullback")

    if "RANGE" in regime:
        recommended += ["MEAN_REVERSION", "LIQUIDITY"]
        rejected += ["NAIVE_BREAKOUT"]
        reason.append("range regime favors reversion or sweep")

    if "VOLATILITY_EXPANSION" in volatility or "DISPLACEMENT" in footprint:
        recommended += ["BREAKOUT", "SMART_MONEY"]
        reason.append("displacement/vol expansion supports breakout and structure logic")

    if "SWEEP" in footprint or "LIQUIDITY" in lifecycle:
        recommended += ["REVERSAL", "COUNTER_TREND", "LIQUIDITY"]
        reason.append("liquidity sweep supports reversal/counter-trend logic")

    if "EXHAUSTION" in lifecycle or "FAILED" in lifecycle:
        recommended += ["REVERSAL", "MEAN_REVERSION"]
        rejected += ["LATE_TREND_FOLLOWING"]
        reason.append("exhaustion/failure suggests reversal/reversion, not late chasing")

    unique_rec = []
    for x in recommended:
        if x not in unique_rec:
            unique_rec.append(x)

    unique_rej = []
    for x in rejected:
        if x not in unique_rej:
            unique_rej.append(x)

    return {
        "recommended_families": "|".join(unique_rec) if unique_rec else "OBSERVE_ONLY",
        "rejected_families": "|".join(unique_rej) if unique_rej else "",
        "router_reason": "; ".join(reason) if reason else "insufficient context",
    }


def context_score(regime_score: float, lifecycle_score: float, event: Dict, context: Optional[Dict]) -> float:
    volume_ratio = fnum(event.get("tick_volume_ratio_50"))
    body_atr = fnum(event.get("body_atr"))
    range_atr = fnum(event.get("range_atr"))
    efficiency = fnum(context.get("post_efficiency")) if context else 0

    score = 0
    score += regime_score * 0.30
    score += lifecycle_score * 0.35
    score += min(volume_ratio * 10, 15)
    score += min(body_atr * 8, 10)
    score += min(range_atr * 5, 10)
    score += min(efficiency * 2, 10)

    return round(min(score, 100), 6)


def context_key(event: Dict) -> str:
    return "|".join([
        event.get("symbol", "DE40"),
        event.get("timeframe", ""),
        event.get("time", ""),
        str(event.get("event_index", "")),
        event.get("event_type", ""),
    ])


def build_context_lookup(context_rows: List[Dict]) -> Dict[str, Dict]:
    lookup = {}
    for r in context_rows:
        key = "|".join([
            r.get("symbol", "DE40"),
            r.get("timeframe", ""),
            r.get("time", ""),
            str(r.get("event_index", "")),
            r.get("event_type", ""),
        ])
        lookup[key] = r
    return lookup


def build_xray_router(events_path: Path, context_path: Path, dataset_root: Path, outdir: Path, max_events: int = 50000) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    events = load_csv(events_path)
    contexts = load_csv(context_path)
    ctx_lookup = build_context_lookup(contexts)

    if max_events > 0:
        events = events[:max_events]

    dataset_cache = {}
    routed_rows = []
    matrix_rows = []
    library_rows = []

    for ev in events:
        tf = ev.get("timeframe", "")
        idx = int(fnum(ev.get("event_index"), 0))
        if tf not in TIMEFRAMES:
            continue

        if tf not in dataset_cache:
            p = dataset_for_tf(dataset_root, tf)
            dataset_cache[tf] = load_candles(p, None) if p else []

        candles = dataset_cache[tf]
        if not candles or idx >= len(candles) or idx < 120:
            continue

        regime = classify_regime(candles, idx)
        ctx = ctx_lookup.get(context_key(ev))
        lifecycle = classify_lifecycle(ev, ctx)
        router = recommended_families(
            regime["regime"],
            lifecycle["lifecycle"],
            ev.get("event_type", ""),
            regime["volatility"],
        )
        score = context_score(regime["score"], lifecycle["lifecycle_score"], ev, ctx)

        permission = "PAPER_CANDIDATE_ALLOWED" if score >= 70 else "OBSERVE_ONLY"
        if score < 55:
            permission = "BLOCK_LOW_CONTEXT_SCORE"

        row = {
            "symbol": ev.get("symbol", "DE40"),
            "timeframe": tf,
            "time": ev.get("time", ""),
            "event_index": idx,
            "event_type": ev.get("event_type", ""),
            "footprint_direction": ev.get("direction", ""),
            "institutional_footprint": "INFERRED_NOT_CONFIRMED",
            "session": ev.get("session", ""),
            "regime": regime["regime"],
            "trend": regime["trend"],
            "volatility": regime["volatility"],
            "regime_score": regime["score"],
            "lifecycle": lifecycle["lifecycle"],
            "lifecycle_score": lifecycle["lifecycle_score"],
            "context_score": score,
            "recommended_families": router["recommended_families"],
            "rejected_families": router["rejected_families"],
            "router_reason": router["router_reason"],
            "paper_permission": permission,
            "mode": MODE,
            "real_orders": REAL_ORDERS,
            "ftmo_real": FTMO_REAL,
            "warning": "ROUTER_OUTPUT_IS_NOT_TRADE_ORDER",
        }

        for k in ["sma20", "sma50", "sma100", "atr14", "rsi14", "distance_to_sma20_atr", "spread_sma20_sma50_atr"]:
            row[k] = regime.get(k, "")

        for k in ["post_mfe_atr", "post_mae_atr", "post_efficiency"]:
            row[k] = lifecycle.get(k, "")

        routed_rows.append(row)

        library_rows.append({
            "context_id": f"DE40::{tf}::{idx}",
            "symbol": "DE40",
            "timeframe": tf,
            "session": row["session"],
            "regime": row["regime"],
            "trend": row["trend"],
            "volatility": row["volatility"],
            "footprint": row["event_type"],
            "lifecycle": row["lifecycle"],
            "recommended_families": row["recommended_families"],
            "context_score": row["context_score"],
            "post_mfe_atr": row["post_mfe_atr"],
            "post_mae_atr": row["post_mae_atr"],
            "outcome_label": "FAVORABLE_AFTER_FOOTPRINT" if fnum(row["post_mfe_atr"]) > fnum(row["post_mae_atr"]) else "ADVERSE_AFTER_FOOTPRINT",
            "memory_use": "STATISTICAL_CONTEXT_LIBRARY",
        })

    grouped = defaultdict(list)
    for r in routed_rows:
        grouped[(r["timeframe"], r["regime"], r["lifecycle"])].append(r)

    for (tf, regime, lifecycle), arr in grouped.items():
        scores = [fnum(x["context_score"]) for x in arr]
        allowed = [x for x in arr if x["paper_permission"] == "PAPER_CANDIDATE_ALLOWED"]
        fam_counter = defaultdict(int)
        for x in arr:
            for fam in str(x["recommended_families"]).split("|"):
                if fam:
                    fam_counter[fam] += 1

        top_family = sorted(fam_counter.items(), key=lambda x: x[1], reverse=True)[0][0] if fam_counter else ""

        matrix_rows.append({
            "symbol": "DE40",
            "timeframe": tf,
            "regime": regime,
            "lifecycle": lifecycle,
            "events": len(arr),
            "avg_context_score": round(sum(scores) / len(scores), 6) if scores else 0,
            "max_context_score": round(max(scores), 6) if scores else 0,
            "paper_allowed_events": len(allowed),
            "paper_allowed_rate": round(len(allowed) / len(arr), 6) if arr else 0,
            "top_recommended_family": top_family,
            "matrix_use": "MULTI_TIMEFRAME_CONTEXT_ROUTING_PRIOR",
        })

    routed_rows = sorted(routed_rows, key=lambda x: fnum(x["context_score"]), reverse=True)
    matrix_rows = sorted(matrix_rows, key=lambda x: (fnum(x["avg_context_score"]), fnum(x["events"])), reverse=True)
    library_rows = sorted(library_rows, key=lambda x: fnum(x["context_score"]), reverse=True)

    files = {
        "router": outdir / "de40_regime_first_xray_router_events.csv",
        "matrix": outdir / "de40_multitimeframe_context_matrix.csv",
        "library": outdir / "de40_institutional_context_library.csv",
        "paper_candidates": outdir / "de40_router_paper_candidate_contexts.csv",
        "blocked": outdir / "de40_router_blocked_contexts.csv",
        "summary_json": outdir / "summary.json",
    }

    write_csv(files["router"], routed_rows)
    write_csv(files["matrix"], matrix_rows)
    write_csv(files["library"], library_rows)
    write_csv(files["paper_candidates"], [x for x in routed_rows if x["paper_permission"] == "PAPER_CANDIDATE_ALLOWED"])
    write_csv(files["blocked"], [x for x in routed_rows if x["paper_permission"] != "PAPER_CANDIDATE_ALLOWED"])

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "events_source": str(events_path),
        "context_source": str(context_path),
        "dataset_root": str(dataset_root),
        "events_loaded": len(events),
        "router_events_generated": len(routed_rows),
        "matrix_rows": len(matrix_rows),
        "context_library_rows": len(library_rows),
        "paper_candidate_contexts": len([x for x in routed_rows if x["paper_permission"] == "PAPER_CANDIDATE_ALLOWED"]),
        "blocked_contexts": len([x for x in routed_rows if x["paper_permission"] != "PAPER_CANDIDATE_ALLOWED"]),
        "architecture": [
            "REGIME_FIRST",
            "XRAY_FOOTPRINT",
            "INSTITUTIONAL_LIFECYCLE",
            "MULTI_TIMEFRAME_CONTEXT_MATRIX",
            "FAMILY_ROUTER",
            "CONTEXT_LIBRARY",
            "PAPER_ONLY_PERMISSION_GATE",
        ],
        "status": "CERTIFIED",
        "certification": "P2377_REGIME_FIRST_XRAY_LIFECYCLE_ROUTER_CERTIFIED",
        "next": "P2378_DE40_ROUTER_PAPER_BACKTEST_AND_PROMOTION_GATE",
        "outputs": {k: str(v) for k, v in files.items()},
        "warning": "NO_REAL_ORDER_PERMISSION_CREATED",
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--events", required=True)
    p.add_argument("--context", required=True)
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-events", type=int, default=50000)
    args = p.parse_args()

    result = build_xray_router(
        Path(args.events),
        Path(args.context),
        Path(args.dataset_root),
        Path(args.outdir),
        args.max_events,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
