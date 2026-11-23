"""Fail-closed trade-level provenance gate; no strategy certification."""
from datetime import datetime
REQUIRED=('edge_id','symbol','timeframe','signal_id','strategy_source_sha256','entry_time','exit_time','signal_time','side','pnl_r','source_ohlc_sha256')
def validate(rows,allowed_edges,symbol='GER40',timeframe='M15'):
 seen=set();count=0
 for row in rows:
  if not all(row.get(k) not in (None,'') for k in REQUIRED):raise ValueError('MISSING_PROVENANCE')
  if row['edge_id'] not in allowed_edges or row['symbol']!=symbol or row['timeframe']!=timeframe:raise ValueError('UNKNOWN_EDGE_OR_MARKET')
  if row['side'] not in ('BUY','SELL'):raise ValueError('INVALID_SIDE')
  if any(len(row[k])!=64 or any(c not in '0123456789abcdef' for c in row[k].lower()) for k in ('strategy_source_sha256','source_ohlc_sha256')):raise ValueError('INVALID_HASH')
  if (row['edge_id'],row['signal_id']) in seen:raise ValueError('DUPLICATE_SIGNAL')
  seen.add((row['edge_id'],row['signal_id']))
  try:
   s=datetime.fromisoformat(row['signal_time']);e=datetime.fromisoformat(row['entry_time']);x=datetime.fromisoformat(row['exit_time']);pnl=float(row['pnl_r'])
  except (ValueError,TypeError):raise ValueError('INVALID_EVENT') from None
  if not s<=e<x or not (-1e9<pnl<1e9):raise ValueError('LOOKAHEAD_OR_NONFINITE')
  if row.get('execution_mode')!='PAPER_ONLY' or row.get('real_execution_allowed') not in (False,'false','False','0'):raise ValueError('UNSAFE_EXECUTION')
  count+=1
 if not count:raise ValueError('EMPTY_SERIES')
 return {'schema_valid':True,'rows':count,'signal_provenance_verified':False,'strategy_replay_certified':False,'portfolio_correlation_certified':False,'runtime_promotion_allowed':False}
