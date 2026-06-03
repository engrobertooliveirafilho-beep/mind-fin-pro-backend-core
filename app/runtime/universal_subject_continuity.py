
from __future__ import annotations
_STATE={}
def norm(x): return (x or '').lower().strip()
def detect_subject(msg):
    t=norm(msg)
    rules=[('vehicle','pickup',['ram 2500','ram 3500','hilux','ranger']),('vehicle','motorcycle',['crf 450','crf','cb500']),('vehicle','car',['corolla','civic','onix']),('animal','dog',['cane corso','bulldog']),('agribusiness','livestock',['confinamento','gado','boi']),('legal','document',['contrato']),('technology','system',['render','supabase','webhook'])]
    for d,c,ks in rules:
        for k in ks:
            if k in t: return {'domain':d,'entity_class':c,'subject':k.upper() if k.startswith('ram') else k}
    return None
def is_followup(msg):
    t=norm(msg); return any(x in t for x in ['vale a pena','quanto ela','quanto ele','por litro','manutencao','manutenção','e depois','aprofund','prossiga','continue'])
def update_subject_state(sender_id,msg):
    sid=sender_id or 'default'; found=detect_subject(msg)
    if found: _STATE[sid]=found; return found
    if sid in _STATE and is_followup(msg): return _STATE[sid]
    if sid in _STATE and norm(msg) in ['oi','bom dia','boa tarde','boa noite','tudo bem']: return _STATE[sid]
    return _STATE.get(sid)
def get_subject_state(sender_id): return _STATE.get(sender_id or 'default')
def reset_subject_state(sender_id='default'): _STATE.pop(sender_id,None)
