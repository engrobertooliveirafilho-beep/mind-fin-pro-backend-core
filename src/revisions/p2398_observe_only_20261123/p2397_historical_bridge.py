"""Read-only P2397 historical evidence bridge; no runtime promotion."""
import csv
import json
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
    return evaluate_research(edge,policy,rows)
