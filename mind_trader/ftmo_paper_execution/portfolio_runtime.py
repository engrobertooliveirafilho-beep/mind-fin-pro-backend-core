"""Deterministic PAPER-only portfolio; no broker APIs."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Dict
from .ftmo_paper_guard import D,PaperAccount,Rules
from .ftmo_pretrade_v2 import OrderIntent,pretrade
@dataclass
class Position:
    side: str
    entry: Decimal
    stop: Decimal
    quantity: Decimal
    point_value: Decimal
    cost: Decimal
    last_price: Decimal
class PaperPortfolio:
    def __init__(self,rules:Rules,day:date):
        self.account=PaperAccount.create(rules,day)
        self.positions:Dict[str,Position]={}
        self.next_id=1
        self.audit=[]
    def _pnl(self,p):
        direction=D(1) if p.side=='BUY' else D(-1)
        return (p.last_price-p.entry)*direction*p.quantity*p.point_value-p.cost
    def _mark_all(self):
        return self.account.mark(sum((self._pnl(p) for p in self.positions.values()),D(0)))
    def _stop_risk(self):
        total=D(0)
        for p in self.positions.values():
            direction=D(1) if p.side=='BUY' else D(-1)
            stop_move=(p.stop-p.last_price)*direction*p.quantity*p.point_value
            total+=max(D(0),-stop_move)
        return total
    def open(self,order:OrderIntent,buffer=0):
        self._mark_all()
        decision=pretrade(self.account,order,existing_stop_risk=self._stop_risk(),buffer=buffer)
        if not decision.allowed:
            self.audit.append({'event':'REJECT','reason':decision.reason})
            return None
        pid=f'PAPER_{self.next_id:06d}'
        self.next_id+=1
        self.positions[pid]=Position(order.side,order.entry,order.stop,order.quantity,order.point_value,order.roundtrip_cost,order.entry)
        self._mark_all()
        self.audit.append({'event':'OPEN','id':pid})
        return pid
    def mark(self,prices):
        if set(prices)!=set(self.positions): raise ValueError('full position mark required')
        values={k:D(v) for k,v in prices.items()}
        if any(not v.is_finite() or v<=0 for v in values.values()): raise ValueError('invalid mark')
        for pid,price in values.items(): self.positions[pid].last_price=price
        ok=self._mark_all()
        self.audit.append({'event':'MARK','equity':str(self.account.equity),'risk_ok':ok})
        return ok
    def close(self,pid,exit_price):
        if pid not in self.positions: raise KeyError(pid)
        exit_price=D(exit_price)
        if not exit_price.is_finite() or exit_price<=0: raise ValueError('invalid exit')
        p=self.positions[pid]
        p.last_price=exit_price
        pnl=self._pnl(p)
        self.account.balance+=pnl
        self.account.trades+=1
        del self.positions[pid]
        self._mark_all()
        self.audit.append({'event':'CLOSE','id':pid,'pnl':str(pnl)})
        return pnl
    def new_day(self,day:date):
        self._mark_all()
        self.account.new_day(day)
        self.audit.append({'event':'NEW_DAY','day':day.isoformat(),'equity':str(self.account.equity)})
    def snapshot(self):
        self._mark_all()
        return {'account':self.account.status(),'open_positions':len(self.positions),'events':len(self.audit),'real_orders':0}
