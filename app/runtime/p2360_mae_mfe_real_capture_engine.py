from __future__ import annotations

def calculate_mae_mfe(trade: dict, price_path: list[float]) -> dict:
    entry = float(trade["entry_price"])
    side = trade["side"].upper()
    exit_price = float(trade.get("exit_price", price_path[-1] if price_path else entry))

    if not price_path:
        return {
            "mae": 0.0,
            "mfe": 0.0,
            "exit_efficiency": 0.0,
            "status": "NO_PRICE_PATH",
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
        }

    if side == "BUY":
        excursions = [p - entry for p in price_path]
        final_move = exit_price - entry
    else:
        excursions = [entry - p for p in price_path]
        final_move = entry - exit_price

    mae = min(excursions)
    mfe = max(excursions)

    exit_efficiency = 0.0
    if mfe > 0:
        exit_efficiency = max(0.0, min(1.0, final_move / mfe))

    return {
        "symbol": trade.get("symbol", ""),
        "side": side,
        "entry_price": entry,
        "exit_price": exit_price,
        "mae": round(mae, 8),
        "mfe": round(mfe, 8),
        "final_move": round(final_move, 8),
        "exit_efficiency": round(exit_efficiency, 4),
        "status": "MAE_MFE_CALCULATED",
        "lesson": classify_trade_lesson(mae, mfe, final_move),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def classify_trade_lesson(mae: float, mfe: float, final_move: float) -> str:
    if mfe > 0 and final_move <= 0:
        return "PROFIT_WAS_AVAILABLE_BUT_NOT_CAPTURED"
    if mae < 0 and abs(mae) > abs(final_move):
        return "TRADE_SUFFERED_ADVERSE_EXCURSION"
    if mfe > 0 and final_move / mfe < 0.5:
        return "EXIT_TOO_LATE_OR_PARTIAL_MISSING"
    if final_move > 0:
        return "TRADE_MANAGED_ACCEPTABLY"
    return "NO_CLEAR_EDGE"

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2360_MAE_MFE_REAL_CAPTURE_ENGINE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
