"""Offline regression suite for S20 authority evidence gate."""
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("authority", ROOT / "src" / "revisions" / "s20_authority_evidence_audit.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
FACTORY_SHA = "3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42"

def fixtures():
    obj = {"canonical_factory":{"sha256":FACTORY_SHA},"canonical_writer":{"sha256":FACTORY_SHA,"symbol_capable":False},"s20_symbol_present":False}
    source = json.dumps(obj, sort_keys=True).encode()
    import hashlib
    cert = {"authority_spec_sha256":hashlib.sha256(source).hexdigest().upper(),"canonical_factory_sha256":FACTORY_SHA,"s20_symbol_present":False}
    return source,json.dumps(cert).encode()

class TestAuthority(unittest.TestCase):
    def test_evidence(self):
        s,c=fixtures()
        self.assertTrue(m.audit_authority(s,c)["evidence_consistent"])
    def test_no_writer_proof(self):
        s,c=fixtures()
        self.assertFalse(m.audit_authority(s,c)["writer_bytes_verified"])
    def test_no_runtime(self):
        s,c=fixtures()
        self.assertFalse(m.audit_authority(s,c)["runtime_allowed"])
    def test_no_s21(self):
        s,c=fixtures()
        self.assertFalse(m.audit_authority(s,c)["s21_certified"])
    def test_mutation(self):
        s,c=fixtures()
        with self.assertRaises(ValueError):m.audit_authority(s+b" ",c)
    def test_wrong_writer(self):
        s,c=fixtures()
        with self.assertRaises(ValueError):m.audit_authority(s,c,b"fake")
    def test_missing(self):
        s,c=fixtures()
        with self.assertRaises(ValueError):m.audit_authority(None,c)
    def test_symbol_forgery(self):
        s,c=fixtures()
        d=json.loads(s);d["s20_symbol_present"]=True
        with self.assertRaises(ValueError):m.audit_authority(json.dumps(d).encode(),c)

class TestFactoryVsWriter(unittest.TestCase):
    def test_factory_evidence_never_proves_writer(self):
        s,c=fixtures()
        result=m.audit_authority(s,c)
        self.assertFalse(result["writer_bytes_verified"])
        self.assertFalse(result["factory_bytes_verified"])
    def test_unverified_factory_bytes_rejected(self):
        s,c=fixtures()
        with self.assertRaises(ValueError): m.audit_authority(s,c,b"fake factory")

class TestOriginalDriveEvidence(unittest.TestCase):
    def test_historical_original_bytes_and_certificate(self):
        root = pathlib.Path(__file__).resolve().parents[1] / "tests" / "fixtures"
        original = (root / "s20_canonical_factory_authority_spec_20260810.json").read_bytes()
        certificate = (root / "s20_canonical_factory_authority_certificate_20260810.json").read_bytes()
        import hashlib
        self.assertEqual(hashlib.sha256(original).hexdigest().upper(), m.EXPECTED_SPEC_SHA)
        result = m.audit_authority(original, certificate)
        self.assertTrue(result["evidence_consistent"])
        self.assertFalse(result["factory_bytes_verified"])
        self.assertFalse(result["writer_bytes_verified"])
        self.assertFalse(result["s21_certified"])
