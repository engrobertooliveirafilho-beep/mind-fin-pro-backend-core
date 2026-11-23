"""Offline paper-order risk interlock. Not a broker adapter or FTMO certification."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True)
class Limits:
    max_daily_loss: Decimal = Decimal('0.04')
    max_total_loss: Decimal = Decimal('0.08')
    max_trade_risk: Decimal = Decimal('0.0075')
    max_open_positions: int = 3
    max_correlated_positions: int = 2


def _number(value):
    if isinstance(value, bool):
        raise ValueError('boolean not numeric')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError('invalid numeric input')
    if not result.is_finite():
        raise ValueError('nonfinite input')
    return result


def authorize_paper_order(order, state, limits=Limits()):
    """Return deny-by-default decision. Paper only; never sends an order."""
    deny = lambda reason: {'approved': False, 'reason': reason, 'mode': 'PAPER_ONLY', 'real_orders_authorized': False}
    if not isinstance(order, dict) or not isinstance(state, dict):
        return deny('INVALID_INPUT')
    if order.get('mode') != 'PAPER' or state.get('mode') != 'PAPER':
        return deny('NON_PAPER_MODE')
    if state.get('authority_verified') is not True or state.get('risk_guard_wired') is not True:
        return deny('AUTHORITY_NOT_VERIFIED')
    if state.get('kill_switch') is not False or state.get('force_no_trade') is not False:
        return deny('TRADING_DISABLED')
    if not isinstance(order.get('symbol'), str) or not order['symbol'].strip():
        return deny('INVALID_SYMBOL')
    try:
        balance = _number(state['initial_balance'])
        equity = _number(state['equity'])
        day_start = _number(state['day_start_equity'])
        risk = _number(order['risk_amount'])
        open_positions = state['open_positions']
        correlated = state['correlated_positions']
        if any(type(x) is not int or x < 0 for x in (open_positions, correlated)):
            return deny('INVALID_POSITION_COUNTS')
        if min(balance, equity, day_start) <= 0 or risk <= 0:
            return deny('INVALID_BALANCE_OR_RISK')
    except (KeyError, ValueError, TypeError):
        return deny('INVALID_NUMERIC_STATE')
    if open_positions >= limits.max_open_positions or correlated >= limits.max_correlated_positions:
        return deny('POSITION_LIMIT')
    # Conservative check uses the initial balance for both loss thresholds.
    if day_start - equity + risk >= balance * limits.max_daily_loss:
        return deny('DAILY_LOSS_LIMIT')
    if balance - equity + risk >= balance * limits.max_total_loss:
        return deny('TOTAL_LOSS_LIMIT')
    if risk > balance * limits.max_trade_risk:
        return deny('TRADE_RISK_LIMIT')
    return {'approved': True, 'reason': 'PAPER_SIMULATION_ONLY', 'mode': 'PAPER_ONLY', 'real_orders_authorized': False}
