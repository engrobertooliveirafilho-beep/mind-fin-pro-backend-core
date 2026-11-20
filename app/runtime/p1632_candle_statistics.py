"""P1632 offline descriptive statistics over validated P1619 historical snapshots."""
from collections import Counter
from .p1619_snapshot_reconciler import WEIGHTS, reconcile

def summarize(rows):
    audit = reconcile(rows)
    if audit['status'] != 'RECONCILED':
        raise ValueError('historical candle scores not reconciled')
    counts = {key: sum(row[key] for row in rows) for key in WEIGHTS}
    by_timeframe = dict(sorted(Counter(row['timeframe'] for row in rows).items()))
    return {'status':'DESCRIPTIVE_ONLY','observations':len(rows),
            'pattern_counts':counts,'timeframe_counts':by_timeframe,
            'nonzero_scores':audit['active_scores'],
            'outcome_labels_available':False,'win_rate':None,
            'statistical_edge_certified':False,'promotion_allowed':False,
            'order_send_allowed':False,'e2e_certified':False}
