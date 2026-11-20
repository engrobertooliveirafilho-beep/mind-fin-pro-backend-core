"""P1100-1500 read-only guard. Does not execute strategies or orders."""
def audit(runtime_report, regimes, portfolio, risk_decision):
    if not isinstance(runtime_report,dict) or not isinstance(regimes,list) or not isinstance(portfolio,list) or not isinstance(risk_decision,dict):
        raise ValueError('invalid inputs')
    for item in [runtime_report,*regimes,*portfolio]:
        if not isinstance(item,dict) or item.get('REAL_ORDERS')!='FORBIDDEN' or item.get('FTMO_REAL')!='FORBIDDEN' or item.get('MT5_REAL')!='FORBIDDEN':
            raise ValueError('unsafe historical artifact')
    if runtime_report.get('ORDER_SENT') is not False:raise ValueError('orders in history')
    if risk_decision.get('status') not in ('REJECTED_CAP','PASS'):raise ValueError('unknown risk decision')
    unvalidated=[x.get('regime') for x in regimes if x.get('status')=='IMPLEMENTED' and not x.get('validation_evidence_sha256')]
    unsafe_keep=[x.get('edge_id') for x in portfolio if x.get('action')=='KEEP' and risk_decision['status']!='PASS']
    return {'status':'BLOCKED_VALIDATION' if unvalidated or unsafe_keep else 'REVIEW_REQUIRED','unvalidated_regimes':unvalidated,'unsafe_keep':unsafe_keep,'module_certification':'UNVERIFIED','order_send_allowed':False,'e2e_certified':False}
