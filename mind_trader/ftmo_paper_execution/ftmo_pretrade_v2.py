"""PAPER-only pretrade guard."""
from dataclasses import dataclass
from decimal import Decimal
from .ftmo_paper_guard import D, PaperAccount
@dataclass(frozen=True)
class OrderIntent:
    side: str
    entry: Decimal
    stop: Decimal
    quantity: Decimal
    point_value: Decimal
    roundtrip_cost: Decimal = Decimal('0')
@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    worst_case_loss: Decimal
    daily_headroom: Decimal
    total_headroom: Decimal
def pretrade(account: PaperAccount,order: OrderIntent,existing_stop_risk=0,buffer=0)->Decision:
    zero=D(0)
    daily_floor=max(account.day_start_balance,account.day_start_equity)-account.rules.initial_balance*account.rules.daily_loss_fraction
    total_floor=account.rules.initial_balance*(D(1)-account.rules.max_loss_fraction)
    daily_headroom=account.equity-daily_floor
    total_headroom=account.equity-total_floor
    def reject(reason,risk=zero): return Decision(False,reason,risk,daily_headroom,total_headroom)
    if account.halted or not account.check(): return reject('HALTED')
    if order.side not in ('BUY','SELL'): return reject('INVALID_SIDE')
    values=[order.entry,order.stop,order.quantity,order.point_value,order.roundtrip_cost,D(existing_stop_risk),D(buffer)]
    if not all(x.is_finite() for x in values): return reject('NONFINITE_INPUT')
    if order.entry<=0 or order.stop<=0 or order.quantity<=0 or order.point_value<=0 or order.roundtrip_cost<0 or D(existing_stop_risk)<0 or D(buffer)<0: return reject('INVALID_INPUT')
    if (order.side=='BUY' and order.stop>=order.entry) or (order.side=='SELL' and order.stop<=order.entry): return reject('INVALID_STOP')
    loss=abs(order.entry-order.stop)*order.quantity*order.point_value+order.roundtrip_cost
    projected=loss+D(existing_stop_risk)+D(buffer)
    if projected>=daily_headroom or projected>=total_headroom: return reject('RISK_BUDGET_EXCEEDED',projected)
    return Decision(True,'PAPER_ONLY',projected,daily_headroom,total_headroom)
