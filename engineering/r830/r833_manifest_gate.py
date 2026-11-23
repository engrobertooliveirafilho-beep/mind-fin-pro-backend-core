"""Offline P4.64C manifest gate; never imports project modules."""
import json
BUCKETS=('ACTIVE_IN_PIPELINE','ACTIVE_IN_WHATSAPP_ADAPTER','ACTIVE_OUTSIDE_PIPELINE','ORPHANED_OR_UNUSED')
def reconcile(raw):
    try:
        obj=json.loads(raw) if isinstance(raw,str) else raw
        buckets=obj['buckets']
        if not isinstance(buckets,dict) or set(buckets)!=set(BUCKETS): raise ValueError('bucket mismatch')
        seen=set()
        counts={}
        for name in BUCKETS:
            modules=buckets[name]
            if not isinstance(modules,list) or any(not isinstance(x,str) or not x.startswith('app.') for x in modules): raise ValueError('invalid module')
            if len(set(modules))!=len(modules) or seen.intersection(modules): raise ValueError('duplicate module')
            seen.update(modules)
            counts[name]=len(modules)
        if obj.get('counts')!=counts: raise ValueError('count mismatch')
        policy=obj['policy']
        if policy.get('delete_files') is not False or policy.get('orphaned_modules_policy')!='do_not_integrate_without_explicit_revalidation': raise ValueError('policy mismatch')
        return {'valid':True,'counts':counts,'total':len(seen),'orphan_promotion_allowed':False}
    except (ValueError,KeyError,TypeError,AttributeError) as e:
        return {'valid':False,'error':type(e).__name__,'orphan_promotion_allowed':False}
