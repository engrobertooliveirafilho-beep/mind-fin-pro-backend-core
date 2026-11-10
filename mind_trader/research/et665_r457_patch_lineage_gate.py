"""ET665 R457 fail-closed P2381 patch lineage validator (read-only)."""
def verify(original_feedback,patched):
    index={r['signal_id']:r for r in original_feedback}
    if len(index)!=len(original_feedback):return False,'DUPLICATE_FEEDBACK'
    if len({r['signal_id'] for r in patched})!=len(patched):return False,'DUPLICATE_PATCH'
    for r in patched:
        prior=index.get(r.get('signal_id'))
        if prior is None:return False,'NO_ORIGINAL_SIGNAL'
        if any(r.get(k)!=v for k,v in prior.items()):return False,'UNVERIFIED_MODIFICATION'
        if r.get('mode')!='PAPER_ONLY' or r.get('real_orders')!='FORBIDDEN' or r.get('ftmo_real')!='FORBIDDEN':return False,'UNSAFE_POLICY'
    return False,'NO_INDEPENDENT_POST_PATCH_REPLAY_PROVEN'
