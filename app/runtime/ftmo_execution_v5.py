"""FTMO PAPER V5: recovered Drive engine with prevalidated day rollover.
Drive original: 1Bk-gkLSKK2d2k4DawfhcGLYdOTjSTlcW.
PAPER only; no broker connectivity. Requires original V4 and portfolio dependencies.
"""
from datetime import date
from .ftmo_paper_guard import D
from app.runtime.ftmo_execution_v4 import ExecutionV4


class ExecutionV5(ExecutionV4):
    def process_bar(self, bars, *, day=None):
        if not isinstance(bars, dict) or set(bars) != set(self.portfolio.positions):
            raise ValueError("complete bars required")
        validated = {}
        for pid, bar in bars.items():
            if not isinstance(bar, dict) or set(("open", "high", "low", "close", "target")) - set(bar):
                raise ValueError("missing OHLC or target")
            try:
                vals = [D(bar[k]) for k in ("open", "high", "low", "close", "target")]
            except (TypeError, ValueError, ArithmeticError, KeyError) as exc:
                raise ValueError("invalid OHLC") from exc
            o, h, l, c, t = vals
            if not all(v.is_finite() and v > 0 for v in vals) or l > min(o, c) or h < max(o, c) or l > h:
                raise ValueError("invalid OHLC")
            validated[pid] = bar
        if day is not None:
            if not isinstance(day, date):
                raise ValueError("invalid day")
            if day < self.portfolio.account.day:
                raise ValueError("time reversal")
            if day > self.portfolio.account.day:
                self.portfolio.new_day(day)
        return super().process_bar(validated)
