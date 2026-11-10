"""Isolated, deterministic PAPER-only cashflow calculation component."""
from decimal import Decimal, InvalidOperation

def money(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError('invalid monetary input')
    try:
        d = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('invalid monetary input') from exc
    if not d.is_finite() or d < 0 or d.as_tuple().exponent < -2:
        raise ValueError('invalid monetary input')
    return d

def run_dry(payload):
    if not isinstance(payload, dict) or set(payload) != {'revenue','fixed_costs','variable_costs','cash_balance'}:
        raise ValueError('invalid cashflow payload')
    vals = {key: money(value) for key,value in payload.items()}
    net = vals['revenue']-vals['fixed_costs']-vals['variable_costs']
    burn = -net if net < 0 else Decimal('0')
    runway = None if burn == 0 else (vals['cash_balance']/burn).quantize(Decimal('0.01'))
    return {'agent_id':'business.strategy_cashflow_agent','status':'processed','mode':'paper_only',
            'component':'monthly_cashflow', 'net_cashflow':str(net.quantize(Decimal('0.01'))),
            'runway_months':str(runway) if runway is not None else None,
            'real_orders':'FORBIDDEN','promotion_authorized':False}
