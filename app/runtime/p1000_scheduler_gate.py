"""Fail-closed validation of historical P1000 scheduler evidence."""
def validate(report, run, upstream):
    if not all(isinstance(x,dict) for x in (report,run,upstream)):
        raise ValueError('invalid input')
    for source in (report,run):
        for key in ('REAL_ORDERS','FTMO_REAL','MT5_REAL'):
            if source.get(key)!='FORBIDDEN':raise ValueError('unsafe scheduler')
        if source.get('ORDER_SEND_ALLOWED') is not False:raise ValueError('orders enabled')
    if report.get('MODE')!='DAILY_AUTONOMOUS_RESEARCH_AND_DEMO_EVIDENCE':raise ValueError('unsafe mode')
    if not isinstance(run.get('TIMESTAMP'),str) or not run['TIMESTAMP']:raise ValueError('missing timestamp')
    if upstream.get('e2e_certified') is not False or upstream.get('order_send_allowed') is not False:raise ValueError('unsafe upstream')
    return {'status':'BLOCKED_UPSTREAM','scheduler_activation_allowed':False,'order_send_allowed':False,'e2e_certified':False}
