"""Read-only P2397 historical evidence bridge; no runtime promotion."""
import csv
import json
import hashlib
from pathlib import Path
from p2397_research_gate import evaluate_research

HERE=Path(__file__).resolve().parent

def evaluate_historical_research():
    edge=json.loads((HERE/'p2394_original_summary.json').read_text(encoding='utf-8'))['best_scored_edge']
    policy=json.loads((HERE/'p2397_original_policy.json').read_text(encoding='utf-8'))
    with (HERE/'p2397_original_hypotheses.csv').open(newline='',encoding='utf-8') as handle:
        rows=list(csv.DictReader(handle))
    for row in rows:
        if row.get('paper_only') == 'True':
            row['paper_only']=True
    key=edge.get('key')
    if not isinstance(key,str) or len(key.split('|')) != 4:
        return evaluate_research({},policy,rows)
    session,footprint,_,transition=key.split('|')
    seeds=[key+'|DD_REDUCTION',session+'|'+footprint+'|SESSION_FOCUS',transition+'|TRANSITION']
    expected=['P2397_HYP_'+hashlib.sha256(x.encode()).hexdigest()[:10].upper() for x in seeds]
    if [row.get('hypothesis_id') for row in rows] != expected:
        return evaluate_research({},policy,rows)
    expected_targets=['reduce_max_dd_r_below_3_5',
                      'prioritize '+session+' + '+footprint,transition]
    expected_reasons=['edge has positive expectancy but drawdown penalty blocked promotion',
                      'only surviving WF edge came from this session/footprint zone',
                      'cycle transition survived WF but score remained observed']
    if ([row.get('target') for row in rows] != expected_targets or
            [row.get('reason') for row in rows] != expected_reasons):
        return evaluate_research({},policy,rows)
    return evaluate_research(edge,policy,rows)
