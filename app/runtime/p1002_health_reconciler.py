"""Read-only P1002 health reconciliation. No runtime writes or orders."""
import math

BLOCKS={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}

def reconcile(report, upstream):
    if not isinstance(report,dict) or not isinstance(upstream,dict):raise ValueError('invalid input')
    if any(report.get(k)!=v for k,v in BLOCKS.items()):raise ValueError('unsafe historical report')
    free=report.get('DISK_FREE_GB'); logs=report.get('LOGS_TOTAL')
    if isinstance(free,bool) or not isinstance(free,(int,float)) or not math.isfinite(free) or free<0:raise ValueError('invalid disk')
    if isinstance(logs,bool) or not isinstance(logs,int) or logs<0:raise ValueError('invalid logs')
    if logs>0 and not report.get('LATEST_LOG'):raise ValueError('missing log evidence')
    if upstream.get('e2e_certified') is not False or upstream.get('order_send_allowed') is not False:raise ValueError('upstream not fail-closed')
    return {'HEALTH':'RED' if upstream.get('certification')=='BLOCKED_UPSTREAM' else 'AMBER', 'CERTIFICATION':'BLOCKED_UPSTREAM','E2E_CERTIFIED':False,'ORDER_SEND_ALLOWED':False,**BLOCKS}
