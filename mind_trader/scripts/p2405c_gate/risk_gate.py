import math

def hard_gate(metrics):
    keys=('pf','winrate','expectancy','max_dd_r','edge_count')
    try:
        p,w,e,d,n=(metrics[k] for k in keys)
        if not all(type(x) in (int,float) and math.isfinite(x) for x in (p,w,e,d,n)):
            return False
        return 1.5<=p<999 and 45<=w<=100 and e>0 and 0<=d<=18 and n>=5 and int(n)==n
    except (KeyError,TypeError,ValueError,OverflowError):
        return False

def runtime_allowed():
    return False
