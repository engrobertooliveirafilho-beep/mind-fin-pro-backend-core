"""P1638 proposed bridge (not recovered original). Offline, read-only and fail-closed."""
from decimal import Decimal, InvalidOperation
from .p1637_session_threshold_gate import reconcile

def bridge(refined, sessions, report, master):
    evidence = reconcile(refined, sessions, report)
    if not isinstance(master, dict) or master.get('DECISION') != 'WATCH_ONLY' or master.get('ORDER_SENT') is not False:
        raise ValueError('unsafe master portfolio state')
    if any(master.get(k) != 'FORBIDDEN' for k in ('REAL_ORDERS','FTMO_REAL','MT5_REAL')):
        raise ValueError('unsafe master flags')
    if not refined or any(row.get('refined_decision') != 'WATCH_ONLY' for row in refined):
        raise ValueError('promotion requires separate certification')
    top = refined[0]
    if not isinstance(master.get('BEST'), dict):
        raise ValueError('missing master best')
    best = master['BEST']
    if best.get('specialist_id') != top.get('specialist_id'):
        return {'status':'RECONCILIATION_CONFLICT','p1637':evidence,
                'order_send_allowed':False,'promotion_allowed':False,'e2e_certified':False}
    return {'status':'P1638_BRIDGE_OFFLINE_ONLY','specialist_id':top['specialist_id'],
            'refined_score':str(top['refined_opportunity_score']),
            'order_send_allowed':False,'promotion_allowed':False,'e2e_certified':False}
