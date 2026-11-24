import math

def rank_results(results):
    ranked=[]
    for row in results:
        p,t,w,d,n=(row[k] for k in ('pf','trades','winrate','maxdd','netprofit'))
        if not all(math.isfinite(x) for x in (p,t,w,d,n)) or not (0<p<10 and 0<=w<=100 and t>=20 and d>=0):
            continue
        tier='A' if p>=1.60 and t>=40 and w>=45 and d>0 else 'B' if p>=1.35 and t>=35 and w>=40 and d>0 else 'C' if p>=1.15 and t>=30 and d>0 else 'D'
        ranked.append(dict(row,tier=tier,status='RESEARCH',mode='PAPER_ONLY',real_orders='FORBIDDEN'))
    return sorted(ranked,key=lambda r:(-r['pf'],r['symbol'],r['timeframe'],r['strategy'],r['params']))
