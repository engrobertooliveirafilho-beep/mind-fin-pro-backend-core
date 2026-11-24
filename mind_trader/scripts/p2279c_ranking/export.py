import csv, json
from pathlib import Path
from reports import rank_results

def export_reports(result, destination):
    ranked=rank_results(result['results'])
    root=Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    fields=['symbol','timeframe','strategy','params','trades','pf','winrate','payoff','maxdd','netprofit','tier','status','mode','real_orders','dataset']
    def write(name, rows):
        with (root/name).open('x',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    write('p2279c_clean_ranking.csv',ranked)
    for tier in 'ABCD': write(f'tier_{tier}.csv',[r for r in ranked if r['tier']==tier])
    with (root/'blocked_backtests.csv').open('x',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['symbol','timeframe','reason']); w.writerows(result['blocked'])
    summary=dict(clean_results=len(ranked),blocked=len(result['blocked']),mode='PAPER_ONLY',real_orders='FORBIDDEN',production='BLOCKED')
    (root/'summary.json').write_text(json.dumps(summary),encoding='utf-8')
    return summary
