"""ET665: historical FACTORY provenance gate (not proof of writer implementation).

Never patch or activate a historical writer by matching only its filename.
"""
import hashlib
import pathlib

CANONICAL_FACTORY_SHA256 = "3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42"
CANONICAL_FACTORY_ENTRYPOINT = "run_institutional_wiring"

def verify_factory_bytes(content):
    if not isinstance(content, bytes) or not content:
        raise ValueError("missing factory bytes")
    actual = hashlib.sha256(content).hexdigest().upper()
    if actual != CANONICAL_FACTORY_SHA256:
        raise ValueError("CANONICAL_FACTORY_SHA256_MISMATCH")
    if CANONICAL_FACTORY_ENTRYPOINT.encode("ascii") not in content:
        raise ValueError("CANONICAL_FACTORY_ENTRYPOINT_MISSING")
    return {"sha256":actual,"factory_authority_verified":True,"writer_authority_verified":False,"symbol_capable":False,"runtime_allowed":False}

def verify_factory_path(path):
    p = pathlib.Path(path)
    if not p.is_file():
        raise ValueError("canonical factory file not found")
    return verify_factory_bytes(p.read_bytes())
