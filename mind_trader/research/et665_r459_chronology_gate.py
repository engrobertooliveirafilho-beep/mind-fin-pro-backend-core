"""ET665 R459 — read-only, fail-closed walk-forward chronology audit."""
from datetime import datetime

def audit(windows, results):
    fmt='%Y.%m.%d %H:%M:%S'
    issues=[]
    intervals=[]
    for w in windows:
        try:
            start=datetime.strptime(w['start_time'],fmt)
            end=datetime.strptime(w['end_time'],fmt)
        except (ValueError,KeyError) as e:
            issues.append('INVALID_DATE:'+str(e));continue
        if start>end:issues.append('REVERSED_WINDOW:'+w['window_id'])
        intervals.append((start,end,w['window_id']))
    if len(intervals)!=5:issues.append('WINDOW_COUNT_NOT_FIVE')
    for a,b in zip(intervals,intervals[1:]):
        if a[1]>=b[0]:issues.append('NON_CHRONOLOGICAL_OR_OVERLAP:'+a[2]+'-'+b[2])
    if any(r.get('status')!='REJECT' for r in results):issues.append('UNEXPECTED_PROMOTION')
    return {'windows':len(windows),'groups':len(results),'reversed_windows':sum(s.startswith('REVERSED_WINDOW') for s in issues),'issues':issues,'certified':False,'runtime_permission':'DENIED'}
