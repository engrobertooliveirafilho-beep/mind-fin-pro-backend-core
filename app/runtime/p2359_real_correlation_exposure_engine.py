from __future__ import annotations

USD_PAIRS = {
    "EURUSD": {"USD": -1, "EUR": 1},
    "GBPUSD": {"USD": -1, "GBP": 1},
    "AUDUSD": {"USD": -1, "AUD": 1},
    "NZDUSD": {"USD": -1, "NZD": 1},
    "USDJPY": {"USD": 1, "JPY": -1},
    "USDCHF": {"USD": 1, "CHF": -1},
    "USDCAD": {"USD": 1, "CAD": -1},
}

def normalized_currency_exposure(symbol: str, side: str, lot: float = 0.01) -> dict:
    symbol = symbol.upper()
    side = side.upper()
    base = USD_PAIRS.get(symbol, {})
    multiplier = 1 if side == "BUY" else -1
    return {k: v * multiplier * lot for k, v in base.items()}

def portfolio_exposure(trades: list[dict]) -> dict:
    exposure = {}
    rows = []

    for t in trades:
        symbol = t.get("symbol", "").upper()
        side = t.get("side", "").upper()
        lot = float(t.get("lot", 0.01))
        exp = normalized_currency_exposure(symbol, side, lot)
        rows.append({"symbol": symbol, "side": side, "lot": lot, "currency_exposure": exp})

        for c, v in exp.items():
            exposure[c] = exposure.get(c, 0.0) + v

    max_abs = max([abs(v) for v in exposure.values()] + [0])
    concentration = "HIGH" if max_abs >= 0.03 else "NORMAL"

    return {
        "positions": rows,
        "currency_exposure": exposure,
        "max_abs_currency_exposure": round(max_abs, 4),
        "concentration": concentration,
        "decision": "REDUCE_OR_BLOCK_CORRELATED_EXPOSURE" if concentration == "HIGH" else "APPROVE_EXPOSURE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def correlation_precheck(existing_trades: list[dict], new_trade: dict) -> dict:
    before = portfolio_exposure(existing_trades)
    after = portfolio_exposure(existing_trades + [new_trade])

    blocked = (
        before["concentration"] == "NORMAL"
        and after["concentration"] == "HIGH"
    ) or after["concentration"] == "HIGH"

    return {
        "before": before,
        "after": after,
        "new_trade": new_trade,
        "approved": not blocked,
        "decision": "BLOCK_CORRELATED_EXPOSURE" if blocked else "APPROVE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2359_REAL_CORRELATION_EXPOSURE_ENGINE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
