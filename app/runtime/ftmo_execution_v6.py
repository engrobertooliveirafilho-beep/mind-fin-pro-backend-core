"""PAPER-only conservative intrabar equity breach detection atop V5.

Recovered from Drive EXECUTION_V6 file 170YBYAeaNHlrG8mmCCP_U5-J-6lSPfs2.
Fix: per-bar breach signal, not stale audit-window history. No broker connectivity.
"""
from datetime import date
from .ftmo_execution_v5 import ExecutionV5
from .ftmo_paper_guard import D

class ExecutionV6(ExecutionV5):
    def process_bar(self, bars, *, day=None):
        # Validate all bars before any mutation, including day rollover.
        if not isinstance(bars, dict) or set(bars) != set(self.portfolio.positions):
            raise ValueError('complete bars required')
        validated = {}
        for pid, bar in bars.items():
            if not isinstance(bar, dict) or not {'open','high','low','close','target'} <= set(bar):
                raise ValueError('missing OHLC or target')
            try:
                v = {k:D(bar[k]) for k in ('open','high','low','close','target')}
            except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
                raise ValueError('invalid OHLC') from exc
            if not all(x.is_finite() and x>0 for x in v.values()) or v['low']>min(v['open'],v['close']) or v['high']<max(v['open'],v['close']) or v['low']>v['high']:
                raise ValueError('invalid OHLC')
            validated[pid]=v
        if day is not None and not isinstance(day, date):
            raise ValueError('invalid day')
        if day is not None and day < self.portfolio.account.day:
            raise ValueError('time reversal')
        if day is not None and day > self.portfolio.account.day:
            self.portfolio.new_day(day)
        # Conservative simultaneous adverse marks, not tick reconstruction.
        worst = D(0)
        for pid, bar in validated.items():
            p = self.portfolio.positions[pid]
            adverse = bar['low'] if p.side == 'BUY' else bar['high']
            direction = D(1) if p.side == 'BUY' else D(-1)
            worst += (adverse-p.entry)*direction*p.quantity*p.point_value-p.cost
        account=self.portfolio.account
        daily_floor=max(account.day_start_balance,account.day_start_equity)-account.rules.initial_balance*account.rules.daily_loss_fraction
        total_floor=account.rules.initial_balance*(D(1)-account.rules.max_loss_fraction)
        breach = account.balance+worst <= max(daily_floor,total_floor)
        if breach:
            account.halted=True
            self.portfolio.audit.append({'event':'INTRABAR_RISK_BREACH','worst_equity':str(account.balance+worst)})
        result=super().process_bar(bars)
        result['intrabar_breach']=breach
        return result
