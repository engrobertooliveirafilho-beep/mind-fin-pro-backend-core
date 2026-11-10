"""ET665.R366: stricter Phase B audit. No self-attested approval can certify.

R365's reviewer_approval=True is only an unverified claim. This audit
never certifies without independently validated approval provenance.
"""
from pathlib import Path
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import FRONTS,verify_record

def audit_strict(root,manifest,verified_approvals=None):
    if not isinstance(manifest,dict) or manifest.get("schema")!="ET665.R365.v1" or not isinstance(manifest.get("fronts"),dict):
        raise ValueError("invalid manifest")
    if set(manifest["fronts"])-set(FRONTS):
        raise ValueError("unknown front")
    # No external approval authority is connected. A caller-provided boolean,
    # username or list is not acceptable proof of authenticated review.
    if verified_approvals is not None:
        raise ValueError("untrusted approval injection")
    results={}
    used_hashes=set()
    used_paths=set()
    for front in FRONTS:
        record=manifest["fronts"].get(front)
        if record is None:
            results[front]="MISSING"
            continue
        reason=verify_record(front,record,Path(root))
        if reason is not None:
            results[front]="BLOCKED: "+reason
            continue
        h=record["artifact_sha256"].lower()
        path=(Path(root)/record["artifact_path"]).resolve()
        if h in used_hashes or path in used_paths:
            results[front]="BLOCKED: reused evidence"
            continue
        used_hashes.add(h);used_paths.add(path)
        results[front]="PENDING_AUTHENTICATED_REVIEW"
    return {"status":"FAIL_CLOSED","certified":0,"total":16,
            "evidence_verified":sum(v=="PENDING_AUTHENTICATED_REVIEW" for v in results.values()),
            "fronts":results,"review_authority":"NOT_CONNECTED",
            "promotion_authorized":False,"real_orders":"FORBIDDEN"}
