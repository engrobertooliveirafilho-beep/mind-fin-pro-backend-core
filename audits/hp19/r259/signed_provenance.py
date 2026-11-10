"""Verify signed provenance envelope; does not certify HP19."""
import base64, json, re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
class EvidenceRejected(ValueError): pass
def canonical(m): return json.dumps(m,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def verify_envelope(e,keys):
    if not isinstance(e,dict) or set(e)!={'manifest','key_id','signature'}: raise EvidenceRejected('INVALID_ENVELOPE')
    kid=e['key_id']
    if not isinstance(kid,str) or not re.fullmatch('[A-Za-z0-9_-]{3,80}',kid) or kid not in keys: raise EvidenceRejected('UNTRUSTED_SIGNER')
    m=e['manifest']
    if not isinstance(m,dict) or not isinstance(m.get('run_id'),str) or not isinstance(m.get('runner_id'),str): raise EvidenceRejected('INVALID_MANIFEST')
    if not isinstance(e['signature'],str): raise EvidenceRejected('INVALID_SIGNATURE_ENCODING')
    try:
        sig=base64.b64decode(e['signature'],validate=True)
        if len(sig)!=64: raise ValueError('signature length')
        Ed25519PublicKey.from_public_bytes(keys[kid]).verify(sig,canonical(m))
    except (InvalidSignature,ValueError,TypeError) as ex: raise EvidenceRejected('SIGNATURE_INVALID') from ex
    return {'signature_verified':True,'certified':False,'reason':'INDEPENDENT_BEHAVIORAL_REVIEW_REQUIRED'}
