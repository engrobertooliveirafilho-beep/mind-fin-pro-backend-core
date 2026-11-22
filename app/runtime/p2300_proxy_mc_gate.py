"""P2300 audit: historical proxy Monte Carlo is never a certification gate."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation

REQUIRED = frozenset({'symbol','timeframe','family','confirmation','exit_model','simulations','trades_per_simulation','base_pf_from_segments','worst_segment_pf','pf_mean','pf_p10','dd_p95','risk_of_ruin','decision','mode','real_orders'})

def reconcile_proxy_monte_carlo(rows, *, trade_ledger=None):
    if not isinstance(rows, (list, tuple)) or len(rows) != 4:
        raise ValueError('P2300_INVALID_ROW_COUNT')
    keys = set()
    for row in rows:
        if not isinstance(row, dict) or not REQUIRED.issubset(row):
            raise ValueError('P2300_INVALID_ROW')
        if any(row.get(k) != v for k,v in {'symbol':'GER40','timeframe':'H1','exit_model':'TIME_EXIT','mode':'PAPER_ONLY','real_orders':'FORBIDDEN','decision':'PASS_MONTE_CARLO'}.items()):
            raise ValueError('P2300_UNSAFE_HISTORICAL_RESULT')
        if str(row['simulations']) != '1000' or str(row['trades_per_simulation']) != '100':
            raise ValueError('P2300_UNVERIFIED_SIMULATION_COUNT')
        key = (row['family'], row['confirmation'])
        if key in keys or row['family'] not in ('LIQUIDITY_SWEEP_REVERSAL','VWAP_REVERSION') or row['confirmation'] not in ('MTF_REQUIRED','VOLATILITY_REQUIRED'):
            raise ValueError('P2300_INVALID_STRATEGY')
        keys.add(key)
        for field in ('base_pf_from_segments','worst_segment_pf','pf_mean','pf_p10','dd_p95','risk_of_ruin'):
            try:
                v=Decimal(str(row[field]).replace(',','.'))
            except (InvalidOperation,ValueError,TypeError):
                raise ValueError('P2300_INVALID_METRIC') from None
            if not v.is_finite() or v < 0:
                raise ValueError('P2300_INVALID_METRIC')
    # Historical simulation used a segmented PF proxy, not trade-by-trade returns.
    return {'status':'PROXY_MONTE_CARLO_ONLY','historical_passes':4,'simulations_reported':4000,
            'trade_ledger_used_in_historical_mc':False,'robustness_certified':False,
            'independent_edges_certified':0,'promotion_allowed':False,'paper_only':True,
            'required_next':'REPLAY_MC_FROM_ORIGINAL_TRADE_LEDGER'}
