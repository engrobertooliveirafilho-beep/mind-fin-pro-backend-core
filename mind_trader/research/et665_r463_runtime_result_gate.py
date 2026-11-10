"""ET665 R463: fail-closed recovered agent runtime certification gate."""
BAD={'stub','noop','not_implemented','not implemented','mock','placeholder','simulated'}
def validate_turn(turn):
    if not isinstance(turn,dict):return {'certified':False,'reason':'INVALID_TURN'}
    p=turn.get('profile')
    if not isinstance(p,dict) or p.get('id') in (None,'','fallback'):return {'certified':False,'reason':'FALLBACK_OR_MISSING_PROFILE'}
    ts=turn.get('tools')
    if not isinstance(ts,list) or not ts:return {'certified':False,'reason':'NO_TOOL_EXECUTION'}
    for i,t in enumerate(ts):
        if not isinstance(t,dict) or t.get('ok') is not True or t.get('error'):return {'certified':False,'reason':f'TOOL_FAILED_{i}'}
        v=t.get('payload')
        if not isinstance(v,dict) or not v:return {'certified':False,'reason':f'EMPTY_PAYLOAD_{i}'}
        if str(v.get('status','')).lower().strip() in BAD or any(x in str(v.get('reason','')).lower() for x in BAD):return {'certified':False,'reason':f'STUB_OR_NOOP_{i}'}
        if t.get('kind')=='chat_llm' and 'provider_receipt' not in v:return {'certified':False,'reason':f'UNVERIFIED_LLM_{i}'}
    return {'certified':False,'reason':'MISSING_END_TO_END_COMPONENT_HASH_AND_AGENT_CHAIN'}
