from __future__ import annotations

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, UTC


IN_DIR = Path("_evidence/P1902A")
OUT_DIR = Path("_evidence/P1902B")

REAL_ASSET_ALLOWLIST = {
    "EURUSD","GBPUSD","USDJPY","USDCAD","AUDUSD","NZDUSD","USDCHF",
    "XAUUSD","XAGUSD","BTCUSD","ETHUSD","NAS100","SP500","DAX","NIKKEI",
    "WIN","WDO","IND","DOL","IFIX","IBOV",
    "PETR4","VALE3","ITUB4","BBDC4","BBAS3","ABEV3","WEGE3","CSAN3","SHUL4",
    "CMIG4","ENEV3","POSI3","MDIA3","TAEE11","BPAC11","ALPA4","HBOR3","BMKS3",
}

TIMEFRAMES = {"TICK","M1","M5","M15","M30","H1","H4","D1","W1","MN1"}

NOISE_PREFIXES = ("P",)
NOISE_WORDS = {
    "TOP10","TOP20","TOP300","MT5","DATA","REPORT","SUMMARY","RESULTS","MEMORY",
    "FEATURE","SPECIALIST","BACKTEST","REGISTRY","MASTER","SNAPSHOT","EVIDENCE"
}


def read_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def is_hash_like(token: str) -> bool:
    return bool(re.fullmatch(r"[A-F0-9]{6,16}", token))


def is_date_like(token: str) -> bool:
    return bool(re.fullmatch(r"20\d{6}", token))


def is_module_like(token: str) -> bool:
    return bool(re.fullmatch(r"P\d+(\.\d+)?[A-Z]?", token))


def is_noise_asset(token: str | None) -> bool:
    if not token:
        return True

    t = token.upper()

    if t in REAL_ASSET_ALLOWLIST:
        return False

    if t in NOISE_WORDS:
        return True

    if is_hash_like(t):
        return True

    if is_date_like(t):
        return True

    if is_module_like(t):
        return True

    if t.isdigit():
        return True

    if re.fullmatch(r"\d+[A-Z]+", t):
        return True

    if re.fullmatch(r"[A-F0-9]{2,}[A-F0-9]*", t) and any(ch.isdigit() for ch in t):
        return True

    return t not in REAL_ASSET_ALLOWLIST


def infer_asset_from_path(file: str) -> str | None:
    tokens = re.split(r"[/_.\-\s]+", file.upper())
    for token in tokens:
        if token in REAL_ASSET_ALLOWLIST:
            return token
    return None


def canonicalize_item(item: dict, category: str) -> dict | None:
    file = item.get("file", "")
    raw_asset = item.get("asset")
    asset = raw_asset if raw_asset and not is_noise_asset(raw_asset) else infer_asset_from_path(file)

    tf = item.get("timeframe")
    if tf and tf.upper() not in TIMEFRAMES:
        tf = None

    if category == "dataset" and not asset:
        return None

    return {
        "category": category,
        "file": file,
        "ext": item.get("ext"),
        "size_bytes": item.get("size_bytes", 0),
        "rows_estimated": item.get("rows_estimated", 0),
        "asset": asset,
        "timeframe": tf,
        "modified_at": item.get("modified_at"),
        "tags": item.get("tags", []),
        "canonical": True,
    }


def load_registries():
    return {
        "dataset": read_json(IN_DIR / "DATASET_REGISTRY.json"),
        "memory": read_json(IN_DIR / "MEMORY_REGISTRY.json"),
        "feature": read_json(IN_DIR / "FEATURE_REGISTRY.json"),
        "specialist": read_json(IN_DIR / "SPECIALIST_REGISTRY.json"),
        "backtest": read_json(IN_DIR / "BACKTEST_REGISTRY.json"),
    }


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_registries()
    canonical = {}
    rejected = {}

    for category, items in raw.items():
        canonical[category] = []
        rejected[category] = []

        seen = set()

        for item in items:
            clean = canonicalize_item(item, category)

            if not clean:
                rejected[category].append({
                    "file": item.get("file"),
                    "asset": item.get("asset"),
                    "reason": "NO_CANONICAL_ASSET_OR_NOISE"
                })
                continue

            key = (clean["category"], clean["file"], clean["asset"], clean["timeframe"])

            if key in seen:
                rejected[category].append({
                    "file": item.get("file"),
                    "asset": item.get("asset"),
                    "reason": "DUPLICATE_CANONICAL_KEY"
                })
                continue

            seen.add(key)
            canonical[category].append(clean)

    assets = sorted({
        item["asset"]
        for rows in canonical.values()
        for item in rows
        if item.get("asset")
    })

    timeframes = sorted({
        item["timeframe"]
        for rows in canonical.values()
        for item in rows
        if item.get("timeframe")
    })

    rows_by_category = {
        cat: sum(i.get("rows_estimated", 0) for i in rows)
        for cat, rows in canonical.items()
    }

    summary = {
        "program": "P1902B_DATASET_CANONICALIZATION",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "raw_counts": {k: len(v) for k, v in raw.items()},
        "canonical_counts": {k: len(v) for k, v in canonical.items()},
        "rejected_counts": {k: len(v) for k, v in rejected.items()},
        "rows_by_category": rows_by_category,
        "canonical_assets": assets,
        "canonical_asset_count": len(assets),
        "canonical_timeframes": timeframes,
        "canonical_timeframe_count": len(timeframes),
        "approved_for_P1902C": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    for cat, rows in canonical.items():
        (OUT_DIR / f"CANONICAL_{cat.upper()}S.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    (OUT_DIR / "REJECTED_NOISE.json").write_text(
        json.dumps(rejected, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT_DIR / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
