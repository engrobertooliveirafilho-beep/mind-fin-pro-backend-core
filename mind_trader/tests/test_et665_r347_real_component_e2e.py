import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from mind_trader.scripts.et665_r347_real_component_e2e import run

class TestRealComponentE2E(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input.csv"
        self.output = self.root / "evidence.json"
        self.input.write_text(
            "decision_id,strategy_id,symbol,decision_ts,signal_ts,price_ts,price,source_sha256\n"
            + "d1,s1,EURUSD,100,101,102,1.2," + "a"*64 + "\n",
            encoding="utf-8"
        )
        self.sha = hashlib.sha256(self.input.read_bytes()).hexdigest()

    def test_real_gate_executes_and_writes_evidence(self):
        result = run(self.input, self.sha, self.output)
        self.assertEqual(result["rows"], 1)
        self.assertEqual(json.loads(self.output.read_text())["input_sha256"], self.sha)
        self.assertEqual(result["status"], "STRUCTURAL_ONLY_NOT_OOS_CERTIFIED")

    def test_tamper_fails_closed(self):
        self.input.write_text(self.input.read_text().replace("1.2", "1.3"))
        with self.assertRaisesRegex(ValueError, "snapshot_sha256_mismatch"):
            run(self.input, self.sha, self.output)
        self.assertFalse(self.output.exists())

    def test_missing_independent_hash_fails(self):
        with self.assertRaisesRegex(ValueError, "independent_sha256_required"):
            run(self.input, "", self.output)

    def test_no_overwrite_input(self):
        with self.assertRaisesRegex(ValueError, "evidence_must_not_overwrite_input"):
            run(self.input, self.sha, self.input)
