"""Read-only contract auditor for recovered historical agent outputs."""
import math

class ContractRejected(ValueError):
    pass

FORBIDDEN = {'real_orders','live_trading','execute_trade','gpu_provision','ftmo_real','place_order','send_order'}

def validate_payload(payload):
    if type(payload) is not dict:
        raise ContractRejected('payload must be dict')
    active=set()
    def visit(v,depth=0):
        if depth>16: raise ContractRejected('depth exceeded')
        if type(v) in (dict,list,tuple):
            ident=id(v)
            if ident in active: raise ContractRejected('cycle')
            active.add(ident)
            try:
                if type(v) is dict:
                    for k,x in v.items():
                        if type(k) is not str or k.casefold() in FORBIDDEN: raise ContractRejected('unsafe key')
                        visit(x,depth+1)
                else:
                    for x in v:visit(x,depth+1)
            finally:active.remove(ident)
        elif type(v) is float and not math.isfinite(v):raise ContractRejected('nonfinite number')
        elif type(v) not in (str,int,float,bool,type(None)):raise ContractRejected('unsupported value')
    visit(payload)
    return True

def certify_response(agent_id,result):
    if type(agent_id) is not str or not agent_id:raise ContractRejected('invalid agent id')
    if type(result) is not dict or result.get('agent_id')!=agent_id:raise ContractRejected('identity mismatch')
    if result.get('status')!='ok' or result.get('mode') in ('stub','live','real') or 'error' in result:
        raise ContractRejected('not functional dry-run evidence')
    validate_payload(result)
    return {'agent_id':agent_id,'contract_valid':True,'functional_certified':False,'e2e_certified':False}
