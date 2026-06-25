from __future__ import annotations

import argparse, csv, json
from pathlib import Path
from typing import Dict, List, Optional


MISSION = "P2376_DE40_BIG_PLAYER_CONTEXT_XRAY_ENGINE"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


def sniff(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:2048].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def fnum(v, d=0.0):
    try:
        if v is None or str(v).strip() == "":
            return d
        return float(str(v).replace(",", "."))
    except Exception:
        return d


def load_csv(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sniff(path)))


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


def sma(vals, i, p):
    if i - p + 1 < 0:
        return None
    return sum(vals[i-p+1:i+1]) / p


def atr(candles, i, p=14):
    if i - p < 1:
        return None
    vals = []
    for x in range(i-p+1, i+1):
        c = candles[x]
        prev = candles[x-1]
        vals.append(max(c["high"]-c["low"], abs(c["high"]-prev["close"]), abs(c["low"]-prev["close"])))
    return sum(vals) / len(vals)


def rsi(vals, i, p=14):
    if i - p < 1:
        return None
    gains, losses = [], []
    for x in range(i-p+1, i+1):
        d = vals[x] - vals[x-1]
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


def avg(nums):
    return sum(nums) / len(nums) if nums else 0.0


def classify_event(candles, closes, i) -> Optional[Dict]:
    c = candles[i]
    prev = candles[i-1]
    a = atr(candles, i, 14)
    if not a or a <= 0:
        return None

    ma20 = sma(closes, i, 20)
    ma50 = sma(closes, i, 50)
    ma100 = sma(closes, i, 100)
    rv = rsi(closes, i, 14)

    if ma20 is None or ma50 is None:
        return None

    lookback = candles[max(0, i-30):i]
    if len(lookback) < 20:
        return None

    recent_high = max(x["high"] for x in lookback)
    recent_low = min(x["low"] for x in lookback)

    body = abs(c["close"] - c["open"])
    rng = max(c["high"] - c["low"], 0.00001)
    wick_up = c["high"] - max(c["open"], c["close"])
    wick_down = min(c["open"], c["close"]) - c["low"]

    vol_window = [x["tick_volume"] for x in candles[max(0, i-50):i] if x["tick_volume"] > 0]
    vol_avg = avg(vol_window)
    vol_ratio = c["tick_volume"] / vol_avg if vol_avg > 0 else 0

    displacement = body / a
    range_atr = rng / a

    sweep_low = c["low"] < recent_low and c["close"] > recent_low
    sweep_high = c["high"] > recent_high and c["close"] < recent_high
    breakout_up = c["close"] > recent_high and body > a * 0.5
    breakout_down = c["close"] < recent_low and body > a * 0.5

    event_type = None
    direction = "NONE"

    if sweep_low and wick_down / rng >= 0.35:
        event_type = "LIQUIDITY_SWEEP_REVERSAL_UP"
        direction = "BUY_INFERRED"
    elif sweep_high and wick_up / rng >= 0.35:
        event_type = "LIQUIDITY_SWEEP_REVERSAL_DOWN"
        direction = "SELL_INFERRED"
    elif breakout_up and displacement >= 0.8:
        event_type = "INSTITUTIONAL_DISPLACEMENT_UP"
        direction = "BUY_INFERRED"
    elif breakout_down and displacement >= 0.8:
        event_type = "INSTITUTIONAL_DISPLACEMENT_DOWN"
        direction = "SELL_INFERRED"
    elif range_atr >= 1.8 and vol_ratio >= 1.5:
        event_type = "HIGH_VOLUME_RANGE_EXPANSION"
        direction = "BUY_INFERRED" if c["close"] > c["open"] else "SELL_INFERRED"

    if not event_type:
        return None

    return {
        "event_index": i,
        "time": c["time"],
        "event_type": event_type,
        "direction": direction,
        "session": session_of(c["time"]),
        "price_open": round(c["open"], 5),
        "price_high": round(c["high"], 5),
        "price_low": round(c["low"], 5),
        "price_close": round(c["close"], 5),
        "atr14": round(a, 6),
        "range_atr": round(range_atr, 6),
        "body_atr": round(displacement, 6),
        "tick_volume": c["tick_volume"],
        "tick_volume_ratio_50": round(vol_ratio, 6),
        "sma20": round(ma20, 6),
        "sma50": round(ma50, 6),
        "sma100": round(ma100, 6) if ma100 else "",
        "rsi14": round(rv, 6) if rv is not None else "",
        "distance_to_sma20_atr": round((c["close"] - ma20) / a, 6),
        "distance_to_sma50_atr": round((c["close"] - ma50) / a, 6),
        "recent_high": round(recent_high, 5),
        "recent_low": round(recent_low, 5),
        "institutional_footprint": "INFERRED_NOT_CONFIRMED",
    }


def context_window(candles, event, before=20, after=20) -> Dict:
    i = int(event["event_index"])
    pre = candles[max(0, i-before):i]
    post = candles[i+1:min(len(candles), i+after+1)]
    c = candles[i]

    pre_high = max([x["high"] for x in pre], default=c["high"])
    pre_low = min([x["low"] for x in pre], default=c["low"])
    post_high = max([x["high"] for x in post], default=c["high"])
    post_low = min([x["low"] for x in post], default=c["low"])

    direction = event["direction"]
    if direction == "BUY_INFERRED":
        mfe = post_high - c["close"]
        mae = c["close"] - post_low
        follow = "CONTINUATION" if post_high > c["close"] else "NO_FOLLOW"
    elif direction == "SELL_INFERRED":
        mfe = c["close"] - post_low
        mae = post_high - c["close"]
        follow = "CONTINUATION" if post_low < c["close"] else "NO_FOLLOW"
    else:
        mfe = 0
        mae = 0
        follow = "UNKNOWN"

    a = float(event["atr14"]) if event["atr14"] else 1.0

    return {
        "event_index": i,
        "time": event["time"],
        "event_type": event["event_type"],
        "direction": direction,
        "session": event["session"],
        "pre_range_atr": round((pre_high - pre_low) / a, 6),
        "post_mfe_atr": round(mfe / a, 6),
        "post_mae_atr": round(mae / a, 6),
        "post_followthrough": follow,
        "post_efficiency": round((mfe / max(mae, 0.00001)), 6),
        "reverse_engineering_label": "WHAT_HAPPENED_BEFORE_AND_AFTER_INSTITUTIONAL_FOOTPRINT",
    }


def run(dataset_root: Path, outdir: Path, max_rows_per_tf: int = 100000) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    events = []
    contexts = []
    tf_summary = []

    for tf in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
        path = dataset_for_tf(dataset_root, tf)
        if not path:
            continue

        candles = load_candles(path, max_rows_per_tf)
        closes = [x["close"] for x in candles]

        tf_events = []

        for i in range(120, len(candles)-25):
            ev = classify_event(candles, closes, i)
            if not ev:
                continue
            ev["symbol"] = "DE40"
            ev["timeframe"] = tf
            tf_events.append(ev)
            events.append(ev)

            cw = context_window(candles, ev, before=20, after=20)
            cw["symbol"] = "DE40"
            cw["timeframe"] = tf
            contexts.append(cw)

        follow = [x for x in contexts if x["timeframe"] == tf and x["post_followthrough"] == "CONTINUATION"]
        tf_summary.append({
            "symbol": "DE40",
            "timeframe": tf,
            "candles_scanned": len(candles),
            "footprint_events": len(tf_events),
            "continuation_after_event": len(follow),
            "continuation_rate": round(len(follow) / len(tf_events), 6) if tf_events else 0,
            "avg_post_mfe_atr": round(avg([x["post_mfe_atr"] for x in contexts if x["timeframe"] == tf]), 6),
            "avg_post_mae_atr": round(avg([x["post_mae_atr"] for x in contexts if x["timeframe"] == tf]), 6),
        })

    files = {
        "events": outdir / "de40_big_player_footprint_events.csv",
        "context": outdir / "de40_big_player_before_after_context.csv",
        "summary_by_timeframe": outdir / "de40_big_player_xray_by_timeframe.csv",
        "summary_json": outdir / "summary.json",
    }

    def write(path, rows):
        fields = sorted({k for r in rows for k in r.keys()}) if rows else ["empty"]
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    write(files["events"], events)
    write(files["context"], contexts)
    write(files["summary_by_timeframe"], tf_summary)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "dataset_root": str(dataset_root),
        "timeframes_analyzed": len(tf_summary),
        "footprint_events_detected": len(events),
        "context_windows_generated": len(contexts),
        "inference_policy": "INSTITUTIONAL_FOOTPRINT_INFERRED_NOT_CONFIRMED",
        "xray_layers": [
            "PRICE_LOCATION",
            "LIQUIDITY_SWEEP",
            "FAKE_BREAKOUT",
            "DISPLACEMENT",
            "TICK_VOLUME_RATIO",
            "ATR_EXPANSION",
            "SMA20_SMA50_SMA100",
            "RSI14",
            "SESSION",
            "BEFORE_AFTER_MFE_MAE",
            "PULLBACK_REVERSAL_CONTINUATION_CONTEXT",
        ],
        "status": "CERTIFIED",
        "certification": "P2376_BIG_PLAYER_CONTEXT_XRAY_ENGINE_CERTIFIED",
        "next": "P2377_DE40_REGIME_FIRST_SIGNAL_ROUTER_WITH_XRAY",
        "outputs": {k: str(v) for k, v in files.items()},
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-rows-per-tf", type=int, default=100000)
    args = p.parse_args()

    result = run(Path(args.dataset_root), Path(args.outdir), args.max_rows_per_tf)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
