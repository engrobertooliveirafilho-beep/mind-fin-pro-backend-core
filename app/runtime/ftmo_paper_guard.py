"""Recovered PAPER-only risk guard; Drive 1ugE_FFCfZPeSNJZmcxCxRJcNpFsd2QLk."""
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from decimal import Decimal
D = lambda x: Decimal(str(x))
@dataclass(frozen=True)
class Rules:
    initial_balance: Decimal
    daily_loss_fraction: Decimal
    max_loss_fraction: Decimal
    profit_target_fraction: Decimal
@dataclass
class PaperAccount:
    rules: Rules
    balance: Decimal
    equity: Decimal
    day: date
    day_start_balance: Decimal
    day_start_equity: Decimal
    halted: bool = False
    trades: int = 0
    @classmethod
    def create(cls, rules, day):
        if type(day) is not date: raise ValueError('initial day must be a calendar date')
        if rules.initial_balance <= 0 or not all(D(0)<x<D(1) for x in (rules.daily_loss_fraction,rules.max_loss_fraction,rules.profit_target_fraction)):
            raise ValueError('invalid rules')
        return cls(rules,rules.initial_balance,rules.initial_balance,day,rules.initial_balance,rules.initial_balance)
    def rollover_at(self, instant, account_timezone):
        """PAPER-only account-local calendar rollover; caller must specify IANA zone."""
        if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError('timezone-aware instant required')
        if not isinstance(account_timezone, str) or not account_timezone:
            raise ValueError('IANA account timezone required')
        try:
            local_day = instant.astimezone(ZoneInfo(account_timezone)).date()
        except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
            raise ValueError('invalid IANA account timezone') from exc
        if local_day < self.day:
            raise ValueError('time reversal')
        if local_day == self.day:
            return False
        self.new_day(local_day)
        return True

    def new_day(self, day):
        if type(day) is not date: raise ValueError('day must be a calendar date')
        if day <= self.day: raise ValueError('day must advance')
        self.day=day
        self.day_start_balance=self.balance
        self.day_start_equity=self.equity
        self.check()
    def check(self):
        anchor=max(self.day_start_balance,self.day_start_equity)
        floor=anchor-self.rules.initial_balance*self.rules.daily_loss_fraction
        total=self.rules.initial_balance*(D(1)-self.rules.max_loss_fraction)
        if self.equity<=floor or self.equity<=total:self.halted=True
        return not self.halted
    def mark(self, unrealized_pnl):
        self.equity=self.balance+D(unrealized_pnl)
        return self.check()
    def close_paper_trade(self, side, entry, exit_price, quantity, point_value, commission=0, slippage_cost=0):
        if self.halted:raise RuntimeError('PAPER risk halt')
        if side not in ('BUY','SELL') or D(quantity)<=0 or D(point_value)<=0:raise ValueError('invalid trade')
        direction=D(1) if side=='BUY' else D(-1)
        pnl=(D(exit_price)-D(entry))*direction*D(quantity)*D(point_value)-D(commission)-D(slippage_cost)
        if D(commission)<0 or D(slippage_cost)<0:raise ValueError('invalid costs')
        self.balance+=pnl;self.equity=self.balance;self.trades+=1;self.check()
        return pnl
    def target_reached(self):
        return self.balance>=self.rules.initial_balance*(D(1)+self.rules.profit_target_fraction) and not self.halted
    def status(self):
        return {'balance':str(self.balance),'equity':str(self.equity),'halted':self.halted,'trades':self.trades,'target_reached':self.target_reached(),'real_orders':0}
