"""Fail-closed S21 symbol lineage contract. No broker or file I/O."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class SymbolLineageError(ValueError):
    pass


def propagate_dispatch_symbol(replay: Mapping[str, Any], dispatch: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve the replay's explicit symbol; reject missing or conflicting lineage."""
    if not isinstance(replay, Mapping) or not isinstance(dispatch, Mapping):
        raise SymbolLineageError("S21_INVALID_LINEAGE_PAYLOAD")
    symbol = replay.get("symbol")
    if not isinstance(symbol, str) or not symbol or symbol != symbol.strip():
        raise SymbolLineageError("S21_REPLAY_SYMBOL_MISSING")
    if any(not (ch.isascii() and (ch.isalnum() or ch in "._-")) for ch in symbol):
        raise SymbolLineageError("S21_REPLAY_SYMBOL_INVALID")
    existing = dispatch.get("symbol")
    if existing is not None and existing != symbol:
        raise SymbolLineageError("S21_DISPATCH_SYMBOL_CONFLICT")
    result = dict(dispatch)
    result["symbol"] = symbol
    return result


def validate_writer_symbol(dispatch: Mapping[str, Any], decision: Mapping[str, Any]) -> str:
    """Validate identity at the writer boundary; never infer a symbol from price."""
    if not isinstance(dispatch, Mapping) or not isinstance(decision, Mapping):
        raise SymbolLineageError("S21_INVALID_LINEAGE_PAYLOAD")
    symbol = dispatch.get("symbol")
    if not isinstance(symbol, str) or not symbol:
        raise SymbolLineageError("S21_DISPATCH_SYMBOL_MISSING")
    if decision.get("symbol") != symbol:
        raise SymbolLineageError("S21_WRITER_SYMBOL_CONFLICT")
    return symbol
