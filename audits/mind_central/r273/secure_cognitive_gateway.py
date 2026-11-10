"""R273: deny-only gateway with unique option IDs and positive finite weight total."""
from safe_cognitive_gateway import purpose, explanation, will, GateRejected
from finite_scores import finite_score, InvalidScore
_ALLOWED_PAYLOAD={'purpose':frozenset({'description','scores'}),'explanation':frozenset({'decision_id','action','source','scores'}),'will':frozenset({'options','weights'})}
_ALLOWED_OPTION=frozenset({'id','name','scores'})
_FORBIDDEN_TEXT=('real_orders','ftmo_real','live_trading','production','mt5','order_send','broker')
def _plain_string(value):
    if not isinstance(value,str) or len(value)>256: raise GateRejected('INVALID_TEXT')
    if any(token in value.casefold() for token in _FORBIDDEN_TEXT): raise GateRejected('FORBIDDEN_OPERATION')
def _authorize(kind,payload):
    if not isinstance(payload,dict) or set(payload)-_ALLOWED_PAYLOAD[kind]: raise GateRejected('UNAUTHORIZED_FIELDS')
    if kind=='will':
        options=payload.get('options')
        if not isinstance(options,list) or not options or len(options)>100: raise GateRejected('INVALID_OPTIONS')
        seen=set()
        for opt in options:
            if not isinstance(opt,dict) or set(opt)-_ALLOWED_OPTION: raise GateRejected('UNAUTHORIZED_OPTION_FIELDS')
            for k in ('id','name'):
                if k in opt: _plain_string(opt[k])
            identifier=opt.get('id') or opt.get('name')
            if not identifier or not isinstance(identifier,str) or not identifier.strip(): raise GateRejected('MISSING_OPTION_ID')
            if identifier in seen: raise GateRejected('DUPLICATE_OPTION_ID')
            seen.add(identifier)
        if 'weights' in payload:
            weights=payload['weights']
            if not isinstance(weights,dict): raise GateRejected('INVALID_WEIGHTS')
            try:
                if sum(finite_score(v) for v in weights.values())<=0: raise GateRejected('ZERO_WEIGHT_VECTOR')
            except InvalidScore as exc: raise GateRejected(str(exc)) from exc
    else:
        for key in ('description','decision_id','action','source'):
            if key in payload: _plain_string(payload[key])
def execute(kind,engine,payload):
    if kind not in _ALLOWED_PAYLOAD: raise GateRejected('UNKNOWN_ENGINE')
    _authorize(kind,payload)
    return {'purpose':purpose,'explanation':explanation,'will':will}[kind](engine,payload)
