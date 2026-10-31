"""Independent fail-closed assessment of historical P2369 summary."""
import json
from pathlib import Path

def assess(path, **evidence):
    s=json.loads(Path(path).read_text(encoding='utf-8'))
    required=('independent_hashes','cost_contract','ftmo_accounting','chronological_oos','full_dataset','ci_verified')
    checks={k:evidence.get(k) is True for k in required}
    checks['paper_only']=s.get('mode')=='PAPER_ONLY'
    checks['no_real_orders']=s.get('real_orders')=='FORBIDDEN'
    checks['seven_datasets']=len(s.get('datasets_detected',[]))==7
    checks['no_promotions']=s.get('promoted_candidates')==0
    return {'status':'EVIDENCE_GATES_REPORTED' if all(checks.values()) else 'BLOCKED', 'original_claim':s.get('status'),'checks':checks,'ftmo_ready':False,'promotion_authorized':False,'real_orders':'FORBIDDEN'}
