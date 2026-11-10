"""R258 deny-only provenance consistency gate. Does not authenticate a runner."""
import hashlib, hmac, re
from pathlib import Path
class ProvenanceError(ValueError): pass
def check_provenance(root:Path, manifest:dict, trusted_runners:set[str]):
    if not isinstance(manifest,dict) or set(manifest)!={'run_id','runner_id','entries'}: raise ProvenanceError('INVALID_MANIFEST')
    run_id,runner=manifest['run_id'],manifest['runner_id']
    if not isinstance(run_id,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{8,80}',run_id): raise ProvenanceError('INVALID_RUN_ID')
    if not isinstance(runner,str) or runner not in trusted_runners: raise ProvenanceError('UNRECOGNIZED_RUNNER')
    entries=manifest['entries']
    if not isinstance(entries,list) or len(entries)!=19: raise ProvenanceError('INCOMPLETE_ENTRIES')
    ids=set(); logs=set(); root=root.resolve(strict=True)
    for e in entries:
        if not isinstance(e,dict) or set(e)!={'agent_id','source_sha256','log_file','log_sha256','run_id','runner_id'}: raise ProvenanceError('INVALID_ENTRY')
        agent=e['agent_id']; filename=e['log_file']
        if not isinstance(agent,str) or not re.fullmatch(r'agent_[a-z0-9_]+',agent) or agent in ids: raise ProvenanceError('DUPLICATE_OR_INVALID_AGENT')
        ids.add(agent)
        if not isinstance(filename,str) or not re.fullmatch(r'[A-Za-z0-9_-]+\.log',filename) or filename in logs: raise ProvenanceError('DUPLICATE_OR_UNSAFE_LOG')
        logs.add(filename)
        if e['run_id']!=run_id or e['runner_id']!=runner: raise ProvenanceError('PROVENANCE_MISMATCH')
        for k in ('source_sha256','log_sha256'):
            if not isinstance(e[k],str) or not re.fullmatch('[a-f0-9]{64}',e[k]): raise ProvenanceError('INVALID_DIGEST')
        for path,digest in ((root/(agent+'.py'),e['source_sha256']),(root/filename,e['log_sha256'])):
            if path.is_symlink() or not path.is_file() or path.resolve().parent!=root: raise ProvenanceError('UNSAFE_OR_MISSING_FILE')
            if not hmac.compare_digest(hashlib.sha256(path.read_bytes()).hexdigest(),digest): raise ProvenanceError('DIGEST_MISMATCH')
    raise ProvenanceError('AUTHENTICITY_UNVERIFIED')
