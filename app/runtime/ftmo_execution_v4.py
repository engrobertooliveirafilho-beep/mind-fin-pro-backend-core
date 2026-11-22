"""PAPER-only stop/target execution adapter. No broker connection.

Recovered from Drive EXECUTION_V4 (file 1PUorE7pvNKMNKNNoqUJ07l73jPgB-vgD).
Original SHA256: 32ec8af253054f0d44c1daac6579e4d55b247c6de9f565c54009f596f3ace365.
ET-019 remediation: mark all positions at one bar snapshot before sequential exits.
"""
from .ftmo_paper_guard import D

class ExecutionV4:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def process_bar(self, bars):
        """bars: id -> {open, high, low, close, target}; pessimistic SL-first if both hit."""
        if not isinstance(bars, dict) or set(bars) != set(self.portfolio.positions):
            raise ValueError('complete bars required')
        validated = {}
        for pid, bar in bars.items():
            if not isinstance(bar, dict):
                raise ValueError('invalid bar')
            try:
                vals = {k: D(bar[k]) for k in ('open','high','low','close','target')}
            except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
                raise ValueError('invalid bar') from exc
            if not all(v.is_finite() and v > 0 for v in vals.values()):
                raise ValueError('invalid bar')
            if vals['low'] > min(vals['open'],vals['close']) or vals['high'] < max(vals['open'],vals['close']):
                raise ValueError('invalid OHLC')
            if vals['low'] > vals['high']:
                raise ValueError('invalid range')
            validated[pid] = vals
        exits = []
        marks = {}
        for pid, bar in validated.items():
            p = self.portfolio.positions[pid]
            if p.side == 'BUY':
                stop_hit = bar['low'] <= p.stop
                target_hit = bar['high'] >= bar['target']
                exit_price = min(bar['open'],p.stop) if stop_hit else max(bar['open'],bar['target']) if target_hit else None
            else:
                stop_hit = bar['high'] >= p.stop
                target_hit = bar['low'] <= bar['target']
                exit_price = max(bar['open'],p.stop) if stop_hit else min(bar['open'],bar['target']) if target_hit else None
            if exit_price is not None:
                exits.append((pid,exit_price,'STOP' if stop_hit else 'TARGET'))
            else:
                marks[pid] = bar['close']
        # ET-019: closing positions sequentially re-marks the account. Ensure
        # all positions use this bar's prices before the first close.
        snapshot = dict(marks)
        snapshot.update({pid: price for pid, price, _ in exits})
        if snapshot:
            self.portfolio.mark(snapshot)
        for pid, price, reason in exits:
            self.portfolio.close(pid,price)
            self.portfolio.audit.append({'event':'AUTO_EXIT','id':pid,'reason':reason,'price':str(price)})
        if marks:
            self.portfolio.mark(marks)
        return {'exits':len(exits),'open':len(self.portfolio.positions),'halted':self.portfolio.account.halted,'real_orders':0}
