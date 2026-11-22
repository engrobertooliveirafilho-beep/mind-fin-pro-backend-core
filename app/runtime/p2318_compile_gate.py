"""P2318 historical MetaEditor compilation evidence, not an EA-consumption certificate."""
import re
import hashlib
RESULT = re.compile(r"Result:\s*(\d+) errors?,\s*(\d+) warnings?,\s*(\d+) ms elapsed")
NAMES = {'P2318_compile.log.txt','P2318B_compile.log.txt','P2318B_compile_retry.log.txt'}

def audit_compile_logs(logs):
    if not isinstance(logs,dict) or set(logs)!=NAMES:
        raise ValueError('P2318_MISSING_COMPILE_LOGS')
    evidence={}
    for name,raw in logs.items():
        if not isinstance(raw,bytes):
            raise ValueError('P2318_INVALID_LOG_BYTES')
        try:
            content=raw.decode('utf-16')
        except UnicodeError as exc:
            raise ValueError('P2318_INVALID_LOG_ENCODING') from exc
        results=RESULT.findall(content)
        if len(results)!=1 or tuple(map(int,results[0][:2]))!=(0,0):
            raise ValueError('P2318_COMPILE_NOT_CLEAN')
        evidence[name]={'sha256':hashlib.sha256(raw).hexdigest(),'elapsed_ms':int(results[0][2])}
    return {'status':'HISTORICAL_COMPILE_ONLY','logs_verified':3,'evidence':evidence,
            'source_mq5_recovered':False,'ea_consumption_certified':False,
            'real_orders_authorized':0,'e2e_certified':False}
