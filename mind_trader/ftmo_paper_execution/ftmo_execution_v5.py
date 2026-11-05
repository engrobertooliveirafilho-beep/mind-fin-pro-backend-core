"""PAPER V5: atomic OHLC validation and day rollover."""
from .ftmo_paper_guard import D
from .ftmo_execution_v4 import ExecutionV4
class ExecutionV5(ExecutionV4):
    def process_bar(self,bars,*,day=None):
        if set(bars)!=set(self.portfolio.positions): raise ValueError('complete bars required')
        for pid,b in bars.items():
            if set(('open','high','low','close','target'))-set(b): raise ValueError('missing OHLC or target')
            vals=[D(b[k]) for k in ('open','high','low','close','target')]
            o,h,l,c,t=vals
            if not all(v.is_finite() and v>0 for v in vals) or l>min(o,c) or h<max(o,c) or l>h: raise ValueError('invalid OHLC')
        if day is not None:
            if day<self.portfolio.account.day: raise ValueError('time reversal')
            if day>self.portfolio.account.day: self.portfolio.new_day(day)
        return super().process_bar(bars)
