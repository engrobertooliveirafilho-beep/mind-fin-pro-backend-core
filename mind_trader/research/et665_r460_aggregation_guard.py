"""ET665 R460 — P2383B aggregation fail-closed guard (research only)."""
def authorize(groups, expected_unique=227):
    if len(groups)!=205:return False,'GROUP_COUNT_MISMATCH'
    levels={r['aggregation_level'] for r in groups}
    if len(levels)!=10:return False,'LEVEL_COUNT_MISMATCH'
    for level in levels:
        if sum(int(r['total_samples']) for r in groups if r['aggregation_level']==level)!=expected_unique:return False,'GROUP_MEMBERSHIP_INTEGRITY'
    if any(r['status']!='REJECT' for r in groups):return False,'UNEXPECTED_PROMOTION'
    if any(int(r['passed_windows'])>=4 for r in groups):return False,'REQUIRES_INDEPENDENT_OOS_REPLAY'
    return False,'REUSED_UNDERLYING_227_SIGNALS_AND_ZERO_PROMOTIONS'
