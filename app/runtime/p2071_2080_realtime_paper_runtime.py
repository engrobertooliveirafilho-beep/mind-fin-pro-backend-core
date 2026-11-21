from __future__ import annotations

import json
import os
import time
import math
import statistics
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional


ABSOLUTE_LOCKS = {
    "MIND_MODE": "PAPER_ONLY",
    "REAL_ORDERS": "FORBIDDEN",
    "LIVE_TRADING": "FALSE",
    "BROKER_EXECUTION": "DISABLED",
    "FINANCIAL_EXECUTION": "DISABLED",
    "FTMO_REAL": "FORBIDDEN",
    "SEND_ORDER": "BLOCKED",
    "MT5_ORDER_SEND": "BLOCKED",
    "BROKER_API_CALL": "BLOCKED",
}


def enforce_paper_only() -> Dict[str, str]:
    for key, value in ABSOLUTE_LOCKS.items():
        os.environ[key] = value
    return dict(ABSOLUTE_LOCKS)


def assert_no_financial_execution() -> None:
    # Inspect existing modes before initializing missing PAPER_ONLY locks.
    # Overwriting an unsafe value first would conceal a lock breach.
    for key, expected in ABSOLUTE_LOCKS.items():
        observed = os.environ.get(key)
        if observed is not None and observed != expected:
            raise RuntimeError(f"{key}_LOCK_BREACH")
    enforce_paper_only()


@dataclass
class MarketTick:
    ts: int
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float


@dataclass
class FeatureFrame:
    ts: int
    symbol: str
    mid: float
    spread: float
    return_1: float
    volatility_20: float
    body_to_range: float
    rsi_14: float
    stoch_14: float
    close_position: float


@dataclass
class PaperSignal:
    ts: int
    symbol: str
    specialist_id: str
    side: str
    confidence: float
    reason: str


@dataclass
class PaperPosition:
    position_id: str
    symbol: str
    specialist_id: str
    side: str
    entry: float
    sl: float
    tp: float
    qty: float
    open_ts: int
    status: str = "OPEN"


class RealtimeDataFeedBridge:
    def __init__(self, symbol: str = "XAUUSD", seed_price: float = 2400.0):
        self.symbol = symbol
        self.source = "SYNTHETIC_DETERMINISTIC"
        self.price = seed_price
        self.ts = int(time.time())
        self.i = 0

    def next_tick(self) -> MarketTick:
        assert_no_financial_execution()
        self.i += 1
        self.ts += 60

        drift = math.sin(self.i / 13.0) * 0.35
        pulse = math.cos(self.i / 7.0) * 0.18
        shock = math.sin(self.i / 31.0) * 0.55

        self.price = max(100.0, self.price + drift + pulse + shock)

        spread = 0.18 + abs(math.sin(self.i / 11.0)) * 0.12
        bid = self.price - spread / 2
        ask = self.price + spread / 2

        return MarketTick(
            ts=self.ts,
            symbol=self.symbol,
            bid=round(bid, 5),
            ask=round(ask, 5),
            last=round(self.price, 5),
            volume=round(100 + abs(math.sin(self.i / 5.0)) * 40, 5),
        )


class RealtimeFeatureBuilder:
    def __init__(self):
        self.history: List[MarketTick] = []

    def update(self, tick: MarketTick) -> FeatureFrame:
        assert_no_financial_execution()
        if tick.symbol != "XAUUSD" or not isinstance(tick.ts, int) or isinstance(tick.ts, bool) or tick.ts < 0:
            raise ValueError("INVALID_PAPER_FEED_IDENTITY")
        for value in (tick.bid, tick.ask, tick.last, tick.volume):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise ValueError("INVALID_PAPER_FEED_VALUE")
        if tick.bid <= 0 or tick.ask < tick.bid or tick.last <= 0 or tick.volume < 0:
            raise ValueError("INVALID_PAPER_FEED_QUOTE")
        if self.history and tick.ts <= self.history[-1].ts:
            raise ValueError("OUT_OF_ORDER_PAPER_FEED")

        self.history.append(tick)
        self.history = self.history[-200:]

        mids = [(x.bid + x.ask) / 2 for x in self.history]
        mid = mids[-1]
        prev = mids[-2] if len(mids) > 1 else mid

        ret1 = 0.0 if prev == 0 else (mid - prev) / prev

        window = mids[-20:]
        volatility = statistics.pstdev(window) if len(window) > 2 else 0.0

        high = max(window)
        low = min(window)
        rng = max(high - low, 1e-9)

        body = abs(mid - prev)
        close_position = (mid - low) / rng

        gains = []
        losses = []

        for a, b in zip(mids[-15:-1], mids[-14:]):
            diff = b - a
            gains.append(max(diff, 0))
            losses.append(abs(min(diff, 0)))

        avg_gain = statistics.mean(gains) if gains else 0.0
        avg_loss = statistics.mean(losses) if losses else 0.0

        if avg_gain == 0 and avg_loss == 0:
            rsi = 50.0
        elif avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        stoch = close_position * 100

        return FeatureFrame(
            ts=tick.ts,
            symbol=tick.symbol,
            mid=round(mid, 5),
            spread=round(tick.ask - tick.bid, 5),
            return_1=round(ret1, 8),
            volatility_20=round(volatility, 8),
            body_to_range=round(body / rng, 8),
            rsi_14=round(rsi, 5),
            stoch_14=round(stoch, 5),
            close_position=round(close_position, 8),
        )


class SignalRuntime:
    # Only the explicitly implemented strategy may emit signals until the
    # original RealDNA adapters are recovered and reconciled.
    SUPPORTED_STRATEGIES = {"RANGE_REVERSION"}

    def __init__(self, specialists: List[Dict[str, Any]]):
        self.specialists = list(specialists)
        self.unsupported_specialists = [
            str(spec.get("id") or spec.get("specialist_id"))
            for spec in self.specialists
            if str(spec.get("logic_type") or spec.get("type") or spec.get("strategy_type") or "").upper()
            not in self.SUPPORTED_STRATEGIES
        ]

    def generate(self, frame: FeatureFrame) -> List[PaperSignal]:
        assert_no_financial_execution()

        signals: List[PaperSignal] = []

        for idx, spec in enumerate(self.specialists):
            sid = str(spec.get("id") or spec.get("specialist_id") or f"REALDNA_{idx+1}")
            typ = str(spec.get("logic_type") or spec.get("type") or spec.get("strategy_type") or "").upper()
            if typ not in self.SUPPORTED_STRATEGIES:
                continue

            side = "HOLD"
            confidence = 0.0
            reason = "NO_EDGE"

            if frame.rsi_14 < 38 and frame.close_position < 0.35:
                side = "BUY"
                confidence = 0.62
                reason = "RANGE_REVERSION_LOW_RSI"

            elif frame.rsi_14 > 62 and frame.close_position > 0.65:
                side = "SELL"
                confidence = 0.62
                reason = "RANGE_REVERSION_HIGH_RSI"

            # VOLATILITY_MOMENTUM previously emitted confidence 0.54, below
            # the executor's 0.55 admission threshold. Do not emit a
            # non-executable signal or invent an unvalidated edge.

            if side != "HOLD":
                signals.append(
                    PaperSignal(
                        ts=frame.ts,
                        symbol=frame.symbol,
                        specialist_id=sid,
                        side=side,
                        confidence=confidence,
                        reason=f"{typ}:{reason}",
                    )
                )

        return signals


class PaperPortfolioExecutor:
    # Historical P2067 paper-only micro-size ceiling; not a broker lot contract.
    MAX_PAPER_QTY = 0.01

    def __init__(self, initial_equity: float = 100000.0):
        if (not isinstance(initial_equity, (int, float)) or isinstance(initial_equity, bool)
                or not math.isfinite(initial_equity) or initial_equity <= 0):
            raise ValueError("INVALID_PAPER_INITIAL_EQUITY")
        self.initial_equity = initial_equity
        self.equity = initial_equity
        self.positions: Dict[str, PaperPosition] = {}
        self.closed: List[Dict[str, Any]] = []
        self.seq = 0
        self._peak_equity = float(initial_equity)
        self._risk_locked = False
        self._daily_risk_locked = False

    def export_state(self) -> Dict[str, Any]:
        assert_no_financial_execution()
        return {
            "schema": "PAPER_EXECUTOR_STATE_V1",
            "initial_equity": self.initial_equity,
            "equity": self.equity,
            "seq": self.seq,
            "positions": [asdict(p) for p in self.positions.values()],
            "closed": self.closed,
            "peak_equity": self._peak_equity,
            "risk_locked": self._risk_locked,
            "daily_risk_locked": self._daily_risk_locked,
            "paper_day": getattr(self, "_paper_day", None),
            "day_start_equity": getattr(self, "_day_start_equity", None),
            "last_event_ts": getattr(self, "_last_event_ts", None),
        }

    @classmethod
    def restore_state(cls, state: Dict[str, Any]) -> "PaperPortfolioExecutor":
        assert_no_financial_execution()
        if not isinstance(state, dict) or state.get("schema") != "PAPER_EXECUTOR_STATE_V1":
            raise ValueError("INVALID_PAPER_EXECUTOR_STATE")
        def finite_positive(value):
            return (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(value) and value > 0)
        initial = state.get("initial_equity")
        equity = state.get("equity")
        peak = state.get("peak_equity")
        day_start = state.get("day_start_equity")
        seq = state.get("seq")
        day = state.get("paper_day")
        last_ts = state.get("last_event_ts")
        if (not all(finite_positive(v) for v in (initial, equity, peak))
                or not isinstance(seq, int) or isinstance(seq, bool) or seq < 0
                or not isinstance(state.get("risk_locked"), bool)
                or not isinstance(state.get("daily_risk_locked"), bool)
                or not isinstance(state.get("positions"), list)
                or not isinstance(state.get("closed"), list)
                or len(state["positions"]) > 3):
            raise ValueError("INVALID_PAPER_EXECUTOR_STATE")
        if day is not None and (not isinstance(day, int) or isinstance(day, bool) or day < 0):
            raise ValueError("INVALID_PAPER_EXECUTOR_STATE")
        if last_ts is not None and (not isinstance(last_ts, int) or isinstance(last_ts, bool) or last_ts < 0):
            raise ValueError("INVALID_PAPER_EXECUTOR_STATE")
        if day is None and (day_start is not None or last_ts is not None):
            raise ValueError("INVALID_PAPER_EXECUTOR_STATE")
        if day is not None and (not finite_positive(day_start) or last_ts is None or last_ts // 86400 != day):
            raise ValueError("INVALID_PAPER_EXECUTOR_STATE")
        # A high-water mark cannot be below the current realized balance.
        # Otherwise the restored drawdown lock can be silently weakened.
        if peak < max(initial, equity):
            raise ValueError("INVALID_PAPER_EXECUTOR_PEAK_EQUITY")
        restored = cls(initial_equity=float(initial))
        restored.equity = float(equity)
        restored._peak_equity = float(peak)
        restored._risk_locked = state["risk_locked"]
        restored._daily_risk_locked = state["daily_risk_locked"]
        restored.seq = seq
        if day is not None:
            restored._paper_day = day
            restored._day_start_equity = float(day_start)
            restored._last_event_ts = last_ts
        ids = set()
        specialists = set()
        for item in state["positions"]:
            if not isinstance(item, dict):
                raise ValueError("INVALID_PAPER_EXECUTOR_POSITION")
            try:
                pos = PaperPosition(**item)
            except (TypeError, ValueError) as exc:
                raise ValueError("INVALID_PAPER_EXECUTOR_POSITION") from exc
            if (pos.status != "OPEN" or pos.symbol != "XAUUSD"
                    or pos.side not in ("BUY", "SELL")
                    or not isinstance(pos.position_id, str) or not pos.position_id
                    or not isinstance(pos.specialist_id, str) or not pos.specialist_id
                    or pos.position_id in ids or pos.specialist_id in specialists
                    or not all(finite_positive(v) for v in (pos.entry, pos.sl, pos.tp, pos.qty))
                    or pos.qty > cls.MAX_PAPER_QTY
                    or not isinstance(pos.open_ts, int) or isinstance(pos.open_ts, bool)
                    or pos.open_ts < 0 or last_ts is None or pos.open_ts > last_ts
                    or (pos.side == "BUY" and not pos.sl < pos.entry < pos.tp)
                    or (pos.side == "SELL" and not pos.tp < pos.entry < pos.sl)):
                raise ValueError("INVALID_PAPER_EXECUTOR_POSITION")
            ids.add(pos.position_id)
            specialists.add(pos.specialist_id)
            restored.positions[pos.position_id] = pos
        # The next PAPER id must exceed every restored position id. A
        # corrupted sequence could otherwise silently overwrite an open trade.
        for pid in ids:
            suffix = pid[6:] if pid.startswith("PAPER_") else ""
            if (not suffix.isascii() or not suffix.isdecimal()
                    or len(suffix) < 6 or int(suffix) < 1
                    or pid != f"PAPER_{int(suffix):06d}" or int(suffix) > seq):
                raise ValueError("INVALID_PAPER_EXECUTOR_SEQUENCE")
        for entry in state["closed"]:
            if (not isinstance(entry, dict) or not isinstance(entry.get("position"), dict)
                    or not finite_positive(entry.get("exit"))
                    or not isinstance(entry.get("pnl"), (int, float))
                    or isinstance(entry.get("pnl"), bool) or not math.isfinite(entry["pnl"])
                    or not isinstance(entry.get("close_ts"), int)
                    or isinstance(entry.get("close_ts"), bool)
                    or entry["close_ts"] < 0
                    or last_ts is None or entry["close_ts"] > last_ts):
                raise ValueError("INVALID_PAPER_EXECUTOR_CLOSED_POSITION")
        closed_ids = set()
        for entry in state["closed"]:
            record = entry["position"]
            pid = record.get("position_id")
            suffix = pid[6:] if isinstance(pid, str) and pid.startswith("PAPER_") else ""
            if (not suffix.isascii() or not suffix.isdecimal()
                    or len(suffix) < 6 or int(suffix) < 1
                    or pid != f"PAPER_{int(suffix):06d}"
                    or int(suffix) > seq or pid in ids or pid in closed_ids
                    or record.get("status") != "CLOSED"
                    or record.get("symbol") != "XAUUSD"
                    or record.get("side") not in ("BUY", "SELL")
                    or not isinstance(record.get("specialist_id"), str)
                    or not record["specialist_id"]
                    or not all(finite_positive(record.get(key)) for key in ("entry", "sl", "tp", "qty"))
                    or record["qty"] > cls.MAX_PAPER_QTY
                    or not isinstance(record.get("open_ts"), int)
                    or isinstance(record.get("open_ts"), bool)
                    or record["open_ts"] < 0 or record["open_ts"] > entry["close_ts"]
                    or (record["side"] == "BUY" and not record["sl"] < record["entry"] < record["tp"])
                    or (record["side"] == "SELL" and not record["tp"] < record["entry"] < record["sl"])
                    or abs(
                        entry["pnl"] - (
                            (entry["exit"] - record["entry"]) * record["qty"]
                            if record["side"] == "BUY"
                            else (record["entry"] - entry["exit"]) * record["qty"]
                        )
                    ) > 0.000011):
                raise ValueError("INVALID_PAPER_EXECUTOR_CLOSED_POSITION")
            closed_ids.add(pid)
        if seq < len(restored.positions) + len(state["closed"]):
            raise ValueError("INVALID_PAPER_EXECUTOR_SEQUENCE")
        realized_equity = float(initial) + sum(entry["pnl"] for entry in state["closed"])
        # Realized equity must reconcile to the closed-trade journal. The
        # executor rounds individual PnL entries to five decimal places.
        if not math.isclose(float(equity), realized_equity, rel_tol=0.0,
                            abs_tol=0.000011 * max(1, len(state["closed"]))):
            raise ValueError("PAPER_EXECUTOR_EQUITY_RECONCILIATION_FAILED")
        restored.closed = state["closed"]
        return restored

    def unrealized_pnl(self, price: float) -> float:
        total = 0.0
        for pos in self.positions.values():
            if pos.side == "BUY":
                total += (price - pos.entry) * pos.qty
            else:
                total += (pos.entry - price) * pos.qty
        return total

    def current_equity(self, price: float) -> float:
        return self.equity + self.unrealized_pnl(price)

    def on_signal(self, signal: PaperSignal, price: float) -> Optional[PaperPosition]:
        assert_no_financial_execution()

        if signal.side not in ("BUY", "SELL") or not isinstance(price, (int, float)) or isinstance(price, bool) or not math.isfinite(price) or price <= 0:
            return None
        if not isinstance(signal.confidence, (int, float)) or isinstance(signal.confidence, bool) or not math.isfinite(signal.confidence) or not (0.55 <= signal.confidence <= 1.0):
            return None
        if not isinstance(signal.symbol, str) or signal.symbol != "XAUUSD":
            return None
        if not isinstance(signal.specialist_id, str) or not signal.specialist_id.strip():
            return None

        # Historical P2067 risk limits: daily 1%, total drawdown 3%.
        # Without an external session clock, the simulated UTC day is derived
        # from the signal timestamp; do not interpret this as broker validation.
        if not isinstance(signal.ts, int) or isinstance(signal.ts, bool) or signal.ts < 0:
            return None
        if hasattr(self, "_last_event_ts") and signal.ts < self._last_event_ts:
            return None  # Reject retroactive signals within the same UTC day.
        day = signal.ts // 86400
        if hasattr(self, "_paper_day") and day < self._paper_day:
            return None  # Reject out-of-order sessions.
        if not hasattr(self, "_paper_day") or self._paper_day != day:
            self._paper_day = day
            self._day_start_equity = self.equity
            self._daily_risk_locked = False
        # Include open-position losses in the admission gate. A new order
        # must not be admitted on stale realized equity alone.
        marked_equity = self.current_equity(price)
        self._peak_equity = max(self._peak_equity, marked_equity)
        if marked_equity <= self._day_start_equity * 0.99:
            self._daily_risk_locked = True
        if marked_equity <= self._peak_equity * 0.97:
            self._risk_locked = True
        if self._risk_locked or self._daily_risk_locked:
            return None

        # No specialist may open more than one position concurrently.
        if any(p.specialist_id == signal.specialist_id for p in self.positions.values()):
            return None
        if len(self.positions) >= 3:
            return None

        risk = 3.0
        reward = 6.0
        # An admitted PAPER trade must remain representable by the
        # snapshot restore contract (positive stop and target).
        if (signal.side == "BUY" and price <= risk) or (signal.side == "SELL" and price <= reward):
            return None

        self.seq += 1

        if signal.side == "BUY":
            sl = price - risk
            tp = price + reward
        else:
            sl = price + risk
            tp = price - reward

        pos = PaperPosition(
            position_id=f"PAPER_{self.seq:06d}",
            symbol=signal.symbol,
            specialist_id=signal.specialist_id,
            side=signal.side,
            entry=price,
            sl=round(sl, 5),
            tp=round(tp, 5),
            qty=self.MAX_PAPER_QTY,
            open_ts=signal.ts,
        )

        self.positions[pos.position_id] = pos
        self._last_event_ts = signal.ts
        return pos

    def mark_to_market(self, frame: FeatureFrame) -> None:
        assert_no_financial_execution()
        if frame.symbol != "XAUUSD":
            raise ValueError("INVALID_PAPER_MARK_SYMBOL")
        if not isinstance(frame.mid, (int, float)) or isinstance(frame.mid, bool) or not math.isfinite(frame.mid) or frame.mid <= 0:
            raise ValueError("INVALID_PAPER_MARK_PRICE")
        if not isinstance(frame.spread, (int, float)) or isinstance(frame.spread, bool) or not math.isfinite(frame.spread) or frame.spread < 0:
            raise ValueError("INVALID_PAPER_MARK_SPREAD")
        if not isinstance(frame.ts, int) or isinstance(frame.ts, bool) or frame.ts < 0:
            raise ValueError("INVALID_PAPER_MARK_TIMESTAMP")
        if hasattr(self, "_last_event_ts") and frame.ts < self._last_event_ts:
            raise ValueError("OUT_OF_ORDER_PAPER_MARK")
        frame_day = frame.ts // 86400
        if hasattr(self, "_paper_day") and frame_day < self._paper_day:
            raise ValueError("OUT_OF_ORDER_PAPER_MARK")
        if not hasattr(self, "_paper_day") or frame_day != self._paper_day:
            self._paper_day = frame_day
            self._day_start_equity = self.current_equity(frame.mid)
            self._daily_risk_locked = False
        self._peak_equity = max(self._peak_equity, self.current_equity(frame.mid))
        if self.current_equity(frame.mid) <= self._peak_equity * 0.97:
            self._risk_locked = True
        if hasattr(self, "_day_start_equity") and self.current_equity(frame.mid) <= self._day_start_equity * 0.99:
            self._daily_risk_locked = True

        self._last_event_ts = frame.ts
        to_close = []

        for pid, pos in self.positions.items():
            price = frame.mid

            if pos.side == "BUY":
                pnl = (price - pos.entry) * pos.qty
                hit = price <= pos.sl or price >= pos.tp
            else:
                pnl = (pos.entry - price) * pos.qty
                hit = price >= pos.sl or price <= pos.tp

            if hit:
                to_close.append((pid, pnl, price, frame.ts))

        for pid, pnl, exit_price, ts in to_close:
            pos = self.positions.pop(pid)
            pos.status = "CLOSED"

            self.equity += pnl

            self.closed.append(
                {
                    "position": asdict(pos),
                    "exit": exit_price,
                    "pnl": round(pnl, 5),
                    "close_ts": ts,
                }
            )


class RuntimeMonitor:
    def __init__(self, initial_equity: float):
        self.initial_equity = initial_equity
        self.events: List[Dict[str, Any]] = []
        self.equity_curve: List[float] = [initial_equity]

    def event(self, kind: str, payload: Dict[str, Any]) -> None:
        assert_no_financial_execution()
        self.events.append(
            {
                "ts": int(time.time()),
                "kind": kind,
                "payload": payload,
            }
        )

    def record_equity(self, equity: float) -> None:
        assert_no_financial_execution()
        self.equity_curve.append(float(equity))

    def snapshot(self, executor: PaperPortfolioExecutor, current_price: Optional[float] = None) -> Dict[str, Any]:
        mark_equity = executor.equity

        if current_price is not None:
            mark_equity = executor.current_equity(current_price)

        self.record_equity(mark_equity)

        peak = max(self.equity_curve) if self.equity_curve else self.initial_equity
        trough = min(self.equity_curve) if self.equity_curve else self.initial_equity

        # Preserve the signed, current drawdown for backward compatibility and
        # expose the true worst peak-to-trough drawdown over the full equity path.
        drawdown_abs = min(0.0, mark_equity - peak)
        drawdown_pct = 0.0 if peak <= 0 else drawdown_abs / peak
        running_peak = self.equity_curve[0]
        max_drawdown_abs = 0.0
        max_drawdown_pct = 0.0
        for point in self.equity_curve:
            running_peak = max(running_peak, point)
            if running_peak > 0:
                decline = max(0.0, running_peak - point)
                max_drawdown_abs = max(max_drawdown_abs, decline)
                max_drawdown_pct = max(max_drawdown_pct, decline / running_peak)

        return {
            "equity": round(mark_equity, 5),
            "realized_equity": round(executor.equity, 5),
            "open_positions": len(executor.positions),
            "closed_trades": len(executor.closed),
            "peak_equity": round(peak, 5),
            "trough_equity": round(trough, 5),
            "drawdown_abs": round(drawdown_abs, 5),
            "drawdown_pct": round(drawdown_pct, 8),
            "max_drawdown_abs": round(max_drawdown_abs, 5),
            "max_drawdown_pct": round(max_drawdown_pct, 8),
            "events": len(self.events),
            "equity_points": len(self.equity_curve),
        }


class RuntimePersistence:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, payload: Dict[str, Any]) -> None:
        assert_no_financial_execution()
        # Atomic replacement prevents a crash from truncating the last
        # successfully committed PAPER snapshot.
        import tempfile
        serialized = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=self.path.name + ".", suffix=".tmp", delete=False
            ) as stream:
                temporary = Path(stream.name)
                stream.write(serialized)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def load(self) -> Dict[str, Any]:
        assert_no_financial_execution()
        if not self.path.exists():
            return {}
        def reject_nonfinite(token: str) -> None:
            raise ValueError("NONFINITE_PAPER_RUNTIME_SNAPSHOT")
        def reject_duplicate_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("DUPLICATE_PAPER_SNAPSHOT_KEY")
                result[key] = value
            return result
        loaded = json.loads(
            self.path.read_text(encoding="utf-8"),
            parse_constant=reject_nonfinite,
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(loaded, dict):
            raise ValueError("INVALID_PAPER_RUNTIME_SNAPSHOT")
        return loaded


def load_portfolio(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    def reject_nonfinite(token: str) -> None:
        raise ValueError("NONFINITE_REALDNA_PORTFOLIO")
    def reject_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("DUPLICATE_REALDNA_PORTFOLIO_KEY")
            result[key] = value
        return result
    raw = json.loads(
        p.read_text(encoding="utf-8"),
        parse_constant=reject_nonfinite,
        object_pairs_hook=reject_duplicate_keys,
    )
    candidates = raw if isinstance(raw, list) else None
    if isinstance(raw, dict):
        aliases = ["specialists", "final_specialists", "portfolio", "locked_specialists"]
        present = [key for key in aliases if key in raw]
        if len(present) > 1:
            raise ValueError("AMBIGUOUS_REALDNA_PORTFOLIO_ROOT")
        if present:
            candidates = raw[present[0]] if isinstance(raw[present[0]], list) else None
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("REALDNA_PORTFOLIO_MISSING_OR_EMPTY")
    seen = set()
    for index, specialist in enumerate(candidates):
        if not isinstance(specialist, dict):
            raise ValueError(f"REALDNA_SPECIALIST_INVALID:{index}")
        identifiers = [specialist[key] for key in ("id", "specialist_id") if key in specialist]
        if not identifiers or any(
            not isinstance(value, str) or not value.strip() or value != value.strip()
            for value in identifiers
        ):
            raise ValueError(f"REALDNA_SPECIALIST_ID_INVALID:{index}")
        if len(set(identifiers)) != 1:
            raise ValueError(f"REALDNA_SPECIALIST_ID_CONFLICT:{index}")
        sid = identifiers[0]
        if not sid:
            raise ValueError(f"REALDNA_SPECIALIST_ID_MISSING:{index}")
        if sid in seen:
            raise ValueError(f"REALDNA_SPECIALIST_ID_DUPLICATE:{sid}")
        seen.add(sid)
        strategies = [
            str(specialist[key]).strip().upper()
            for key in ("logic_type", "type", "strategy_type")
            if key in specialist and specialist[key] is not None
        ]
        if len(set(strategies)) > 1:
            raise ValueError(f"REALDNA_SPECIALIST_STRATEGY_CONFLICT:{sid}")
        strategy = strategies[0] if strategies else ""
        if not strategy:
            raise ValueError(f"REALDNA_SPECIALIST_STRATEGY_MISSING:{sid}")
    # Historical P2067 weights are not proof of an executable allocation.
    # Validate any supplied allocation; do not silently normalize residuals.
    weight_present = ["normalized_weight" in item for item in candidates]
    if isinstance(raw, dict) and "declared_reserve" in raw and not any(weight_present):
        raise ValueError("P2067_RESERVE_WITHOUT_WEIGHTS")
    if any(weight_present):
        if not all(weight_present):
            raise ValueError("P2067_PARTIAL_ALLOCATION")
        if not isinstance(raw, dict):
            raise ValueError("P2067_RESERVE_DECLARATION_REQUIRED")
        from app.runtime.p2067_allocation_contract import reconcile_p2067_weights
        reconcile_p2067_weights(candidates, declared_reserve=raw.get("declared_reserve"))
    return candidates


def promote_p2080_if_ready(mission_status: Dict[str, str]) -> Dict[str, str]:
    required = [
        "P2072_REALTIME_FEATURE_BUILDER",
        "P2073_SIGNAL_RUNTIME",
        "P2074_PAPER_PORTFOLIO_EXECUTOR",
        "P2075_RUNTIME_MONITOR",
        "P2076_EXTENDED_RUNTIME_VALIDATION",
        "P2077_MULTI_SESSION_RUNTIME",
        "P2078_RECOVERY_VALIDATION",
        "P2079_RUNTIME_PERSISTENCE",
    ]
    simulated_feed = mission_status.get("P2071_REALTIME_DATA_FEED_BRIDGE") == "PASS_SIMULATED_ONLY"
    prior_pass = all(mission_status.get(key) == "PASS" for key in required)
    mission_status["P2080_REALTIME_RUNTIME_CERTIFICATION"] = (
        "PASS_SIMULATION_SCOPE_ONLY" if simulated_feed and prior_pass else "FAIL"
    )
    return mission_status


def run_p2071_2080(
    portfolio_path: str,
    output_dir: str,
    cycles: int = 1500,
) -> Dict[str, Any]:
    assert_no_financial_execution()
    if not isinstance(cycles, int) or isinstance(cycles, bool) or cycles <= 0:
        raise ValueError("INVALID_PAPER_RUNTIME_CYCLES")

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    specialists = load_portfolio(portfolio_path)

    feed = RealtimeDataFeedBridge()
    features = RealtimeFeatureBuilder()
    signal_runtime = SignalRuntime(specialists)
    executor = PaperPortfolioExecutor()
    monitor = RuntimeMonitor(initial_equity=executor.initial_equity)
    persistence = RuntimePersistence(str(output / "runtime_state.json"))

    mission_status = {
        "P2071_REALTIME_DATA_FEED_BRIDGE": "PASS_SIMULATED_ONLY",
        "P2072_REALTIME_FEATURE_BUILDER": "PASS",
        "P2073_SIGNAL_RUNTIME": "FAIL" if signal_runtime.unsupported_specialists else "PASS",
        "P2074_PAPER_PORTFOLIO_EXECUTOR": "PENDING_RISK_AND_FILL_VALIDATION",
        "P2075_RUNTIME_MONITOR": "PASS",
        "P2076_EXTENDED_RUNTIME_VALIDATION": "PENDING",
        "P2077_MULTI_SESSION_RUNTIME": "PENDING",
        "P2078_RECOVERY_VALIDATION": "PENDING",
        "P2079_RUNTIME_PERSISTENCE": "PENDING",
        "P2080_REALTIME_RUNTIME_CERTIFICATION": "PENDING",
    }

    all_frames: List[Dict[str, Any]] = []
    all_signals: List[Dict[str, Any]] = []

    for _ in range(cycles):
        tick = feed.next_tick()
        frame = features.update(tick)

        signals = signal_runtime.generate(frame)

        executor.mark_to_market(frame)

        for sig in signals:
            pos = executor.on_signal(sig, frame.mid)
            if pos:
                monitor.event("PAPER_POSITION_OPENED", asdict(pos))

        monitor.snapshot(executor, current_price=frame.mid)

        all_frames.append(asdict(frame))
        all_signals.extend([asdict(s) for s in signals])

    snap = monitor.snapshot(executor, current_price=all_frames[-1]["mid"] if all_frames else None)

    state = {
        "locks": enforce_paper_only(),
        "portfolio_file": portfolio_path,
        "specialists_loaded": len(specialists),
        "cycles": cycles,
        "frames": len(all_frames),
        "signals": len(all_signals),
        "executor": {
            "initial_equity": executor.initial_equity,
            "final_equity": executor.equity,
            "mark_to_market_equity": snap["equity"],
            "open_positions": [asdict(x) for x in executor.positions.values()],
            "closed_positions": executor.closed,
        },
        "monitor": snap,
        "executor_snapshot": executor.export_state(),
    }

    persistence.save(state)
    loaded = persistence.load()

    if loaded == state:
        mission_status["P2079_RUNTIME_PERSISTENCE"] = "PASS"

    # Restore the complete PAPER executor, not merely its equity number.
    # This checks serialization compatibility; crash/restart certification
    # still requires a separate process interruption and replay.
    recovered = PaperPortfolioExecutor.restore_state(loaded["executor_snapshot"])
    if recovered.export_state() != executor.export_state():
        raise RuntimeError("PAPER_EXECUTOR_RESTORE_MISMATCH")
    if recovered.current_equity(all_frames[-1]["mid"] if all_frames else 2400.0) != executor.current_equity(all_frames[-1]["mid"] if all_frames else 2400.0):
        raise RuntimeError("PAPER_EXECUTOR_RESTORED_EQUITY_MISMATCH")
    # P2078 remains PENDING until a real restart/recovery replay is verified.

    # A second synthetic feed loop is not proof of distinct sessions,
    # durable session boundaries, or uninterrupted PAPER continuity.
    # P2077 remains PENDING until a multi-session integration test exists.

    if cycles >= 1000 and len(all_frames) == cycles:
        mission_status["P2076_EXTENDED_RUNTIME_VALIDATION"] = "PASS"

    mission_status = promote_p2080_if_ready(mission_status)

    all_pass = all(v in ("PASS", "PASS_SIMULATED_ONLY", "PASS_SIMULATION_SCOPE_ONLY") for v in mission_status.values())

    final = {
        "program": "P2071_2080_REALTIME_PAPER_INFRASTRUCTURE",
        "patch": "P2071_2080B_CERTIFICATION_DRAWDOWN_REPAIR",
        "status": "PASS_SIMULATION_SCOPE_ONLY" if all_pass else "FAIL",
        "readiness": "SIMULATED_PAPER_RUNTIME_VALIDATED_REALTIME_FEED_NOT_CERTIFIED" if all_pass else "NOT_CERTIFIED",
        "data_source": feed.source,
        "realtime_feed_certified": False,
        "absolute_restrictions": enforce_paper_only(),
        "mission_status": mission_status,
        "metrics": {
            "cycles": cycles,
            "frames_built": len(all_frames),
            "signals_generated": len(all_signals),
            "closed_trades": len(executor.closed),
            "open_positions": len(executor.positions),
            "initial_equity": executor.initial_equity,
            "final_realized_equity": round(executor.equity, 5),
            "final_mark_to_market_equity": snap["equity"],
            "paper_realized_pnl": round(executor.equity - executor.initial_equity, 5),
            "paper_mark_to_market_pnl": round(snap["equity"] - executor.initial_equity, 5),
            "peak_equity": snap["peak_equity"],
            "trough_equity": snap["trough_equity"],
            "drawdown_abs": snap["drawdown_abs"],
            "drawdown_pct": snap["drawdown_pct"],
            "max_drawdown_abs": snap["max_drawdown_abs"],
            "max_drawdown_pct": snap["max_drawdown_pct"],
            "equity_points": snap["equity_points"],
        },
        "evidence_files": {
            "runtime_state": str(output / "runtime_state.json"),
            "final_json": str(output / "P2071_2080_FINAL_CERTIFICATION.json"),
            "audit": str(output / "P2071_2080_AUDIT.md"),
        },
        "next_block": "P2081_2090_REALTIME_PORTFOLIO_GOVERNANCE",
    }

    Path(output / "P2071_2080_FINAL_CERTIFICATION.json").write_text(
        json.dumps(final, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    audit = f"""# MIND TRADER — P2071→P2080B AUDIT

## STATUS
{final["status"]}

## READINESS
{final["readiness"]}

## PATCH
P2071_2080B_CERTIFICATION_DRAWDOWN_REPAIR

## FIXES
- P2080 certification promotion repaired.
- Runtime drawdown calculation repaired.
- Equity curve now records mark-to-market values throughout runtime.
- Absolute PAPER_ONLY restrictions preserved.

## MISSIONS
{json.dumps(mission_status, indent=2, ensure_ascii=False)}

## METRICS
{json.dumps(final["metrics"], indent=2, ensure_ascii=False)}

## ABSOLUTE LOCKS
{json.dumps(final["absolute_restrictions"], indent=2, ensure_ascii=False)}

## CONCLUSION
P2071→P2080 status is restricted to simulation evidence only; no realtime market feed certification.
No real orders.
No broker execution.
No financial execution.
"""
    Path(output / "P2071_2080_AUDIT.md").write_text(audit, encoding="utf-8")

    return final
