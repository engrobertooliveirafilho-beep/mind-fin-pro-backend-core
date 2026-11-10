"""Read-only PAPER-only P2379 bus completeness gate."""

def verify(ready,bus):
    a=[r['signal_id'] for r in ready]
    b=[r['signal_id'] for r in bus]
    if len(a)!=len(set(a)) or len(b)!=len(set(b)):return False,'DUPLICATE_ID'
    for r in ready+bus:
        if r.get('mode')!='PAPER_ONLY' or r.get('real_orders')!='FORBIDDEN' or r.get('ftmo_real')!='FORBIDDEN' or r.get('mt5_real_permission')!='DENIED':return False,'UNSAFE_POLICY'
    if set(a)!=set(b):return False,'INCOMPLETE_OR_EXTRA_BUS'
    for r in ready:
        try: pf=float(r.get('profit_factor_proxy','nan'))
        except (ValueError,TypeError):return False,'INVALID_PF'
        if not (0<=pf<999):return False,'UNBOUNDED_PROXY_PF'
    return False,'INDEPENDENT_OOS_AND_COSTS_NOT_PROVEN'
