"""ET665: canonical S20 writer provenance must match historical SHA-256.

Never patch or activate a historical writer by matching only its filename.
"""
import hashlib
import pathlib

CANONICAL_SHA256 = "3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42"
CANONICAL_ENTRYPOINT = "run_institutional_wiring"

def verify_writer_bytes(content):
    if not isinstance(content, bytes) or not content:
        raise ValueError("missing writer bytes")
    actual = hashlib.sha256(content).hexdigest().upper()
    if actual != CANONICAL_SHA256:
        raise ValueError("CANONICAL_WRITER_SHA256_MISMATCH")
    if CANONICAL_ENTRYPOINT.encode("ascii") not in content:
        raise ValueError("CANONICAL_ENTRYPOINT_MISSING")
    return {"sha256":actual,"authority_verified":True,"symbol_capable":False,"runtime_allowed":False}

def verify_writer_path(path):
    p = pathlib.Path(path)
    if not p.is_file():
        raise ValueError("canonical writer file not found")
    return verify_writer_bytes(p.read_bytes())
