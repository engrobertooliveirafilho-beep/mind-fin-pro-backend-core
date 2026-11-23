from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence
FUTURE_ONLY_FIELDS = frozenset({"post_mfe_atr", "post_mae_atr", "post_efficiency", "post_followthrough", "future_mfe", "future_mae", "future_return", "realized_r", "mae_r", "mfe_r"})
class CausalIntegrityError(ValueError): pass
def _utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip(): raise CausalIntegrityError("timestamp ausente")
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise CausalIntegrityError("timestamp ISO-8601 inválido") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed): raise CausalIntegrityError("timestamp deve declarar UTC")
    return parsed.astimezone(timezone.utc)
def validate_decision_payload(features: Mapping[str, Any]) -> None:
    forbidden = sorted(set(features).intersection(FUTURE_ONLY_FIELDS))
    if forbidden: raise CausalIntegrityError("features pós-evento proibidas: " + ",".join(forbidden))
def deterministic_signal_id(*, symbol: str, timeframe: str, event_time: str, family: str, source_row_sha256: str) -> str:
    _utc(event_time)
    if not all(isinstance(x, str) and x.strip() for x in (symbol, timeframe, family, source_row_sha256)): raise CausalIntegrityError("identidade incompleta")
    if len(source_row_sha256) != 64 or any(c not in "0123456789abcdef" for c in source_row_sha256.lower()): raise CausalIntegrityError("source_row_sha256 inválido")
    canonical = "|".join((symbol, timeframe, event_time, family, source_row_sha256.lower()))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
def next_executable_candle_index(*, signal: Mapping[str, Any], candles: Sequence[Mapping[str, Any]]) -> int:
    symbol = signal.get("symbol"); signal_time = _utc(signal.get("event_time", ""))
    if not symbol or not candles: raise CausalIntegrityError("símbolo ou candles ausentes")
    parsed = []
    for candle in candles:
        if candle.get("symbol") != symbol: raise CausalIntegrityError("símbolo do candle divergente")
        parsed.append(_utc(candle.get("time", "")))
    if any(b <= a for a, b in zip(parsed, parsed[1:])): raise CausalIntegrityError("candles devem ser estritamente cronológicos")
    for i, candle_time in enumerate(parsed):
        if candle_time > signal_time: return i
    raise CausalIntegrityError("não existe candle executável posterior ao sinal")
def apply_training_blocks(rows: Iterable[Mapping[str, Any]], blocked_family_timeframe: set[tuple[str, str]]) -> list[dict[str, Any]]:
    kept = []
    for row in rows:
        key = (str(row.get("family", "")), str(row.get("timeframe", "")))
        if key in blocked_family_timeframe: continue
        kept.append(dict(row))
    return kept
def summarize_replay(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    values = [float(row["realized_r"]) for row in rows]
    wins = [x for x in values if x > 0]; losses = [x for x in values if x < 0]
    gross_win = sum(wins); gross_loss = abs(sum(losses))
    pf = gross_win / gross_loss if gross_loss else None
    equity = peak = max_dd = 0.0
    for value in values:
        equity += value; peak = max(peak, equity); max_dd = max(max_dd, peak - equity)
    return {"samples":len(values),"wins":len(wins),"losses":len(losses),"expectancy_r":sum(values)/len(values) if values else None,"gross_win_r":gross_win,"gross_loss_r":gross_loss,"profit_factor":pf,"max_drawdown_r":max_dd,"all_rows_included":True}
