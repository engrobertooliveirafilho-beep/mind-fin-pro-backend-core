"""Offline audit of historical S20 writer authority evidence; never activates runtime."""
import hashlib
import json

EXPECTED_FACTORY_SHA = "3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42"
EXPECTED_SPEC_SHA = "05A8F32790126A0005F5560C9EDD128FCC6C7CBB77B40833CE340E2FDE1CEF16"

def audit_authority(spec_bytes, certificate_bytes, writer_bytes=None):
    if not isinstance(spec_bytes, bytes) or not isinstance(certificate_bytes, bytes):
        raise ValueError("original evidence bytes required")
    spec = json.loads(spec_bytes)
    cert = json.loads(certificate_bytes)
    if not isinstance(spec, dict) or not isinstance(cert, dict):
        raise ValueError("invalid authority evidence")
    if hashlib.sha256(spec_bytes).hexdigest().upper() != cert.get("authority_spec_sha256"):
        raise ValueError("authority spec checksum mismatch")
    factory = spec.get("canonical_factory")
    writer = spec.get("canonical_writer")
    if not isinstance(factory, dict) or not isinstance(writer, dict):
        raise ValueError("missing canonical writer")
    if factory.get("sha256") != EXPECTED_FACTORY_SHA or writer.get("sha256") != EXPECTED_FACTORY_SHA:
        raise ValueError("canonical SHA mismatch")
    if cert.get("canonical_factory_sha256") != EXPECTED_FACTORY_SHA:
        raise ValueError("certificate SHA mismatch")
    if spec.get("s20_symbol_present") is not False or writer.get("symbol_capable") is not False:
        raise ValueError("historical symbol state inconsistent")
    if cert.get("s20_symbol_present") is not False:
        raise ValueError("certificate symbol state inconsistent")
    if writer_bytes is None:
        return {"evidence_consistent":True,"writer_bytes_verified":False,"runtime_allowed":False,"s21_certified":False}
    if not isinstance(writer_bytes, bytes) or hashlib.sha256(writer_bytes).hexdigest().upper() != EXPECTED_FACTORY_SHA:
        raise ValueError("canonical writer bytes mismatch")
    return {"evidence_consistent":True,"writer_bytes_verified":True,"runtime_allowed":False,"s21_certified":False}
