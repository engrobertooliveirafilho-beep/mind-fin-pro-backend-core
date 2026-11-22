from decimal import Decimal

def reconcile(summary, rows, rules):
    symbols=('EURUSD','GBPUSD','USDJPY','USDCHF','USDCAD','XAUUSD','US100','US500','UK100','JP225')
    if summary.get('mode')!='PAPER_ONLY' or summary.get('real_orders')!='FORBIDDEN' or summary.get('ftmo_real')!='FORBIDDEN':
        raise ValueError('UNSAFE_MODE')
    if rules.get('engine_required')!='P2296C_REAL_EXIT_ENGINE_ONLY' or rules.get('dedup_required')!='TRUE' or rules.get('wf_segmented_required')!='TRUE' or rules.get('stress_required')!='TRUE':
        raise ValueError('MISSING_GATES')
    if len(rows)!=10 or {r.get('target_symbol') for r in rows}!=set(symbols):
        raise ValueError('INVALID_SYMBOL_SET')
    for r in rows:
        if r.get('status')!='CANDIDATES_FOUND' or int(r.get('candidate_rows',-1))!=12096 or int(r.get('batches_with_symbol',-1)) not in (25,26):
            raise ValueError('INVALID_CANDIDATES')
    if sum(int(r['candidate_rows']) for r in rows)!=int(summary.get('total_non_ger40_candidates',-1)):
        raise ValueError('COUNT_MISMATCH')
    return {'status':'CANDIDATES_ONLY_NOT_CERTIFIED','candidates':120960,'symbols':10,'tested_edges':0,'promotion_allowed':False,'e2e_certified':False}
