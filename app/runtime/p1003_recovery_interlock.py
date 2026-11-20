"""Read-only recovery decision; never launches orchestrator."""
from pathlib import Path
import hashlib
BLOCKS={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
def assess(historical,upstream,artifacts):
    if not isinstance(historical,dict) or not isinstance(upstream,dict) or not isinstance(artifacts,dict):raise ValueError('invalid input')
    if any(historical.get(k)!=v for k,v in BLOCKS.items()):raise ValueError('unsafe history')
    if upstream.get('e2e_certified') is not False or upstream.get('order_send_allowed') is not False:raise ValueError('unsafe upstream')
    missing=[];altered=[]
    for name,spec in artifacts.items():
        if not isinstance(name,str) or not isinstance(spec,dict) or not isinstance(spec.get('sha256'),str) or len(spec['sha256'])!=64:raise ValueError('invalid manifest')
        path=Path(name)
        if not path.is_file():missing.append(name)
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=spec['sha256']:altered.append(name)
    blocked=bool(missing or altered or upstream.get('certification')!='CERTIFIED')
    return {'status':'BLOCKED' if blocked else 'REVIEW_REQUIRED','recovery_action':'MANUAL_REVIEW_ONLY','automatic_rerun_allowed':False,'order_send_allowed':False,'missing':missing,'altered':altered,**BLOCKS}
