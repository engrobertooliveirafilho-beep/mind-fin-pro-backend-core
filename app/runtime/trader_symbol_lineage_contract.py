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
    if symbol != symbol.strip() or any(
        not (ch.isascii() and (ch.isalnum() or ch in "._-")) for ch in symbol
    ):
        raise SymbolLineageError("S21_DISPATCH_SYMBOL_INVALID")
    if decision.get("symbol") != symbol:
        raise SymbolLineageError("S21_WRITER_SYMBOL_CONFLICT")
    return symbol


def build_symbolized_decision_row(
    replay: Mapping[str, Any],
    dispatch: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a new writer-ready row; never rewrite the historical S20 ledger.

    Fail closed on ambiguous identity and conflicting keys. This does not
    persist anything or certify the canonical writer integration.
    """
    if not isinstance(decision, Mapping):
        raise SymbolLineageError("S21_INVALID_LINEAGE_PAYLOAD")
    routed = propagate_dispatch_symbol(replay, dispatch)
    symbol = validate_writer_symbol(routed, decision)
    row = dict(decision)
    if row.get("symbol") != symbol:
        raise SymbolLineageError("S21_WRITER_SYMBOL_CONFLICT")
    for key in ("day", "tick"):
        upstream = replay.get(key)
        if upstream is None or isinstance(upstream, bool) or not isinstance(upstream, int) or upstream < 0:
            raise SymbolLineageError("S21_REPLAY_IDENTITY_INVALID")
        if dispatch.get(key) != upstream or decision.get(key) != upstream:
            raise SymbolLineageError("S21_LINEAGE_IDENTITY_CONFLICT")
        row[key] = upstream
    row["symbol"] = symbol
    return row
