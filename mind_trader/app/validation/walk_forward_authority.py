import json, statistics, math
from pathlib import Path

def walk_forward_authority(windows):
    blocked = {'passed':False,'production':'BLOCKED','live':'FORBIDDEN','edge_claim':'NONE'}
    if not isinstance(windows,(list,tuple)) or len(windows)<3:
        return dict(blocked,decision='WALK_FORWARD_INSUFFICIENT_WINDOWS')
    try:
        values = [(w['expectancy'],w['profit_factor']) for w in windows]
        if any(type(x) not in (int,float) or not math.isfinite(x) for pair in values for x in pair) or any(p<0 for _,p in values):
            raise ValueError('Invalid metrics')
        expectancies,pfs=zip(*values)
        avg_exp=statistics.mean(expectancies)
        min_pf=min(pfs)
        consistency=sum(x>0 for x in expectancies)/len(windows)
        passed=avg_exp>0 and min_pf>1.05 and consistency>=0.67
    except (TypeError,ValueError,KeyError,OverflowError):
        return dict(blocked,decision='WALK_FORWARD_INVALID_METRICS')
    return dict(blocked,authority='P8.81_WALK_FORWARD_AUTHORITY',windows=len(windows),avg_expectancy=avg_exp,min_profit_factor=min_pf,positive_window_ratio=consistency,passed=passed,decision='WALK_FORWARD_PASS_RESEARCH_ONLY' if passed else 'WALK_FORWARD_REJECT_OR_RETEST')

def save_walk_forward_authority(report,path='mind_trader/reports/P8.81_walk_forward_authority.json'):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    return path
