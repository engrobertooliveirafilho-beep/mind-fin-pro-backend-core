"""Research-only, fail-closed gate. No broker/runtime interface."""
import math

def evaluate(playbook):
    if not isinstance(playbook,dict):return False,'INVALID_RECORD'
    if playbook.get('mode')!='PAPER_ONLY' or playbook.get('real_orders')!='FORBIDDEN' or playbook.get('ftmo_real')!='FORBIDDEN':return False,'UNSAFE_POLICY'
    if playbook.get('promotion_decision')!='PROMOTE_PLAYBOOK':return False,'NOT_PROMOTED'
    if playbook.get('signal_status')!='PAPER_SIGNAL_READY' or playbook.get('direction') not in ('BUY_PAPER','SELL_PAPER'):return False,'NO_VERIFIED_BUS_MATCH'
    try: pf=float(playbook.get('profit_factor_proxy','nan'))
    except (ValueError,TypeError):return False,'INVALID_PROXY_PF'
    if not math.isfinite(pf) or pf>=999:return False,'UNBOUNDED_PROXY_PF'
    return False,'INDEPENDENT_OOS_AND_COSTS_NOT_PROVEN'
