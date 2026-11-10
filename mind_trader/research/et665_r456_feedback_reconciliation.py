"""ET665 R456: read-only P2380 feedback reconciliation, fail closed."""
def reconcile(feedback,bus,demoted):
    fids=[r['signal_id'] for r in feedback]
    bids=[r['signal_id'] for r in bus]
    checks={
        '500_feedback':len(feedback)==500,
        '500_bus':len(bus)==500,
        'unique_feedback':len(set(fids))==len(fids),
        'unique_bus':len(set(bids))==len(bids),
        'exact_ids':set(fids)==set(bids),
        'paper_only':all(r.get('mode')=='PAPER_ONLY' and r.get('real_orders')=='FORBIDDEN' and r.get('ftmo_real')=='FORBIDDEN' and r.get('mt5_real_permission')=='DENIED' for r in feedback+bus),
        'feedback_evaluated':all(r.get('feedback_status')=='EVALUATED' for r in feedback),
        '49_demoted':len(demoted)==49,
        '17_positive_demoted':sum(float(r['expectancy_r'])>0 for r in demoted)==17,
        '5_unbounded_demoted_pf':sum(float(r['profit_factor'])==999 for r in demoted)==5
    }
    pnl=sum(float(r['realized_r']) for r in feedback)
    checks['negative_pnl']=abs(pnl+41.902513)<0.0001
    checks['negative_expectancy']=abs(pnl/500+0.083805)<0.00001
    return {'checks':checks,'passed':sum(checks.values()),'total':len(checks),'net_r':round(pnl,6),'release_allowed':False,'reason':'PROXY_PNL_NOT_INDEPENDENT_OOS_COST_CERTIFIED'}
