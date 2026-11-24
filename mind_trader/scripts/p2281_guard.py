from decimal import Decimal

def pretest(edges):
    # Historical approval is not a current execution authorization.
    return {'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','signals_generated':0,
            'ledger':[{'edge_id':e['edge_id'],'status':'BLOCKED','reason':'UNCERTIFIED_SIGNAL_AND_RISK_STATE'} for e in edges],
            'production':'BLOCKED'}
