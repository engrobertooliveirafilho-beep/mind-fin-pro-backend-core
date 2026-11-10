"""ET665.R289 independent file-integrity gate for research evidence.

This verifies bytes against declared SHA256. It does NOT prove signal causality.
No broker, network, runtime promotion or external execution.
"""
import hashlib
from pathlib import Path

def verify_evidence_files(strategy_rule_file, ohlc_file, declared_rule_sha256, declared_ohlc_sha256):
    def check(path, declared):
        if not isinstance(declared, str) or len(declared) != 64:
            return False
        if not all(ch in "0123456789abcdef" for ch in declared.lower()):
            return False
        if not path or not Path(path).is_file():
            return False
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest() == declared.lower()
    rule_ok = check(strategy_rule_file, declared_rule_sha256)
    ohlc_ok = check(ohlc_file, declared_ohlc_sha256)
    return {
        "strategy_rule_integrity": rule_ok,
        "ohlc_integrity": ohlc_ok,
        "integrity_verified": rule_ok and ohlc_ok,
        "causal_signal_verified": False,
        "runtime_promotion_allowed": False,
        "status": "QUARANTINE",
    }
