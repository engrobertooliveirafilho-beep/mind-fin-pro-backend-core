"""Fail-closed audit of historical P2309 PAPER watch portfolio."""
def reconcile(rows, performance, risk):
    if not isinstance(rows, list) or len(rows) != 7:
        raise ValueError('INVALID_PORTFOLIO_ROWS')
    if not isinstance(performance, dict) or not isinstance(risk, dict):
        raise ValueError('INVALID_LEDGER')
    if performance.get('closed_trades') != '0' or performance.get('trades_consumed') != '0':
        raise ValueError('UNVERIFIED_PERFORMANCE')
    if risk.get('portfolio_rows') != '7' or risk.get('unique_symbols') != '4':
        raise ValueError('PORTFOLIO_LEDGER_MISMATCH')
    for row in rows:
        if any(row.get(k) != v for k, v in {'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','lot':'0.01'}.items()):
            raise ValueError('UNSAFE_ROW')
    ger = [r for r in rows if r['symbol'] == 'GER40']
    non = [r for r in rows if r['symbol'] != 'GER40']
    if len(ger) != 4 or len(non) != 3:
        raise ValueError('INVALID_SPLIT')
    if any(r['timeframe'] != 'H1' or r['exit_model'] != 'TIME_EXIT' or r['source'] != 'P2299_APPROVED_EDGE' for r in ger):
        raise ValueError('INVALID_GER40')
    malformed = [r['symbol'] for r in non if r.get('timeframe') == 'D1D1' or r.get('family') == 'EMA_CROSSEMA_CROSS']
    if any(r.get('status') != 'PAPER_WATCH_CANDIDATE_REQUIRES_BACKTEST' for r in non):
        raise ValueError('UNSAFE_CANDIDATE_STATUS')
    return {'status':'P2309_PORTFOLIO_NOT_CERTIFIED','historical_rows':7,'historical_unique_symbols':4,
            'candidate_symbols':3,'malformed_candidate_symbols':malformed,
            'independent_edges_certified':0,'performance_certified':False,'promotion_allowed':False,
            'e2e_certified':False}
