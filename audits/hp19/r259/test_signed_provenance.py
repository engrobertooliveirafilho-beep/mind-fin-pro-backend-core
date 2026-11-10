import base64, copy, unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from signed_provenance import verify_envelope, canonical, EvidenceRejected
class SignedProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.private=Ed25519PrivateKey.generate()
        self.pub=self.private.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        self.manifest={'run_id':'test_run_001','runner_id':'offline_test','entries':[]}
        self.envelope={'manifest':self.manifest,'key_id':'fixture','signature':base64.b64encode(self.private.sign(canonical(self.manifest))).decode()}
    def test_valid_signature_does_not_certify(self):
        result=verify_envelope(self.envelope,{'fixture':self.pub});self.assertTrue(result['signature_verified']);self.assertFalse(result['certified'])
    def test_modified_manifest_rejected(self):
        e=copy.deepcopy(self.envelope);e['manifest']['run_id']='changed'
        with self.assertRaises(EvidenceRejected):verify_envelope(e,{'fixture':self.pub})
    def test_unknown_signer_rejected(self):
        with self.assertRaises(EvidenceRejected):verify_envelope(self.envelope,{})
    def test_wrong_key_rejected(self):
        other=Ed25519PrivateKey.generate().public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
        with self.assertRaises(EvidenceRejected):verify_envelope(self.envelope,{'fixture':other})
    def test_bad_signature_rejected(self):
        e=copy.deepcopy(self.envelope);e['signature']='not base64%%%'
        with self.assertRaises(EvidenceRejected):verify_envelope(e,{'fixture':self.pub})
    def test_missing_field_rejected(self):
        e=copy.deepcopy(self.envelope);del e['signature']
        with self.assertRaises(EvidenceRejected):verify_envelope(e,{'fixture':self.pub})
    def test_invalid_manifest_rejected(self):
        e=copy.deepcopy(self.envelope);e['manifest']={}
        with self.assertRaises(EvidenceRejected):verify_envelope(e,{'fixture':self.pub})
if __name__=='__main__':unittest.main()
