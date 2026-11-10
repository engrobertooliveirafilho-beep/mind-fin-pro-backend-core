"""P2384A static-context fidelity cannot certify independent performance."""
SURVIVOR={'timeframe':'M15','regime':'TREND_DOWN','session':'OFF_SESSION','footprint':'LIQUIDITY_SWEEP_REVERSAL_UP','lifecycle':'LIQUIDITY_REVERSAL_ENTRY'}
def verify(rows):
    if not rows:return False,'NO_RECORDS'
    if len({r.get('time') for r in rows})!=len(rows):return False,'DUPLICATE_TIMES'
    for r in rows:
        if any(r.get(k)!=v for k,v in {'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN'}.items()):return False,'UNSAFE_POLICY'
        exact=all(r.get(k)==v for k,v in SURVIVOR.items())
        if exact != (float(r.get('context_similarity',-1))==100):return False,'SIMILARITY_INCONSISTENT'
    return False,'STATIC_CONTEXT_MATCH_NOT_INDEPENDENT_OOS'
