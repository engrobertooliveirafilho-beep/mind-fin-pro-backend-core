"""ET665 R458: no order execution; deny replay labels without independent market proof."""
def authorize_promotion(before,after):
    if not isinstance(before,dict) or not isinstance(after,dict):return False,'INVALID_INPUT'
    if any(after.get(k)!=v for k,v in {'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN'}.items()):return False,'UNSAFE_POLICY'
    if before.get('signal_id')!=after.get('signal_id'):return False,'IDENTITY_MISMATCH'
    if all(before.get(k)==after.get(k) for k in ('realized_r','entry_price','entry_time','mae_r','mfe_r','paper_result')):
        return False,'HISTORICAL_OUTCOME_REUSED'
    return False,'INDEPENDENT_OOS_COSTS_AND_EXECUTION_NOT_CERTIFIED'
