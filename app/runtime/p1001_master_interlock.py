"""P1001 historical master report gate, no order capability."""
from decimal import Decimal, InvalidOperation

def gate(master, release_decision):
    if not isinstance(master,dict) or not isinstance(release_decision,dict):
        raise ValueError('invalid input')
    for key in ('REAL_ORDERS','FTMO_REAL','MT5_REAL'):
        if master.get(key)!='FORBIDDEN':raise ValueError('unsafe master')
    if master.get('ORDER_SEND_ALLOWED') is not False:raise ValueError('order allowed')
    if release_decision.get('real_ftmo_release_allowed') is not False or release_decision.get('order_sent') is not False:
        raise ValueError('unsafe release decision')
    for key in ('ALLOCATED_EDGES','SUPERVISED_EDGES','POSITIONS_TOTAL'):
        value=master.get(key)
        if isinstance(value,bool) or not isinstance(value,int) or value<0:raise ValueError('invalid count')
    if master['ALLOCATED_EDGES']!=master['SUPERVISED_EDGES'] or master['POSITIONS_TOTAL']!=0:
        raise ValueError('unreconciled positions')
    try: equity=Decimal(str(master['EQUITY']))
    except (KeyError,ValueError,InvalidOperation):raise ValueError('invalid equity')
    if not equity.is_finite() or equity<=0:raise ValueError('invalid equity')
    return {'health':'RED' if release_decision.get('certification')=='BLOCKED_RISK' else 'AMBER',
            'certification':'BLOCKED_UPSTREAM','demo_operation_ready':False,'order_send_allowed':False,
            'real_ftmo_release_allowed':False,'e2e_certified':False,'historical_health':master.get('HEALTH')}
