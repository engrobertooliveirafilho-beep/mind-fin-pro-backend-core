"""ME-RS-303: isolated synthetic POST_R6 regression; no Drive, network or production."""
import hashlib
import importlib.util
import json
import pathlib
import sqlite3
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "code" / "engineering_pipeline" / "post_r6.py"
spec = importlib.util.spec_from_file_location("post_r6_under_test", MODULE)
post = importlib.util.module_from_spec(spec)
spec.loader.exec_module(post)

def h(data):
    return hashlib.sha256(data).hexdigest()

class PostR6Offline(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.source = self.root / "r6.jsonl"
        self.db = self.root / "ledger.sqlite"
        self.raw = []
        for seq in range(1, 5):
            item = dict(stage="R6", seq=seq, r5_seq=seq,
                        r4_sha256=h(("r4-%d" % seq).encode()),
                        r5_sha256=h(("r5-%d" % seq).encode()))
            self.raw.append((json.dumps(item, separators=(",", ":")) + "\n").encode())
        self.source.write_bytes(b"".join(self.raw))

    def approval(self, seq, mismatch=False):
        item = json.loads(self.raw[seq-1])
        return dict(r6_sha256=h(self.raw[seq-1]),
                    r4_sha256=h(b"wrong") if mismatch else item["r4_sha256"],
                    r5_sha256=item["r5_sha256"], decision="APPROVED", authority="synthetic-test")

    def manifest(self, item):
        path = self.root / "approvals.jsonl"
        path.write_text(json.dumps(item) + "\n", encoding="utf-8")
        return path

    def state(self):
        with sqlite3.connect(self.db) as db:
            return db.execute("SELECT seq,decision,authority FROM records ORDER BY seq").fetchall()

    def test_bounded_resume_and_idempotence(self):
        first = post.consume(self.source, self.db, limit=2)
        self.assertEqual((first["processed"], first["total"], first["pending"]), (2, 2, 2))
        second = post.consume(self.source, self.db, limit=2)
        self.assertEqual((second["processed"], second["total"], second["pending"]), (2, 4, 4))
        repeat = post.consume(self.source, self.db, limit=2)
        self.assertEqual((repeat["processed"], repeat["promoted"], repeat["total"]), (0, 0, 4))
        self.assertTrue(all(x[1:] == ("PENDING", None) for x in self.state()))

    def test_late_approval_promotes_only_matching_lineage(self):
        post.consume(self.source, self.db, limit=4)
        result = post.consume(self.source, self.db, self.manifest(self.approval(2)), limit=4)
        self.assertEqual((result["processed"], result["promoted"], result["approved"]), (0, 1, 1))
        self.assertEqual(self.state()[1][1:], ("APPROVED", "synthetic-test"))

    def test_late_approval_lineage_mismatch_rolls_back(self):
        post.consume(self.source, self.db, limit=4)
        before = self.state()
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            post.consume(self.source, self.db, self.manifest(self.approval(2, True)), limit=4)
        self.assertEqual(self.state(), before)

    def test_prefix_mutation_rejected_without_new_rows(self):
        post.consume(self.source, self.db, limit=2)
        before = self.state()
        self.source.write_bytes(self.source.read_bytes().replace(b'"stage"', b'"stAge"', 1))
        with self.assertRaisesRegex(ValueError, "SOURCE_PREFIX_CHANGED"):
            post.consume(self.source, self.db, limit=2)
        self.assertEqual(self.state(), before)

    def test_partial_tail_is_not_consumed(self):
        self.source.write_bytes(self.raw[0] + self.raw[1][:-1])
        result = post.consume(self.source, self.db, limit=4)
        self.assertEqual((result["processed"], result["total"]), (1, 1))
        self.assertEqual(len(self.state()), 1)

    def test_invalid_next_record_rolls_back(self):
        post.consume(self.source, self.db, limit=2)
        before = self.state()
        corrupt = json.loads(self.raw[2])
        corrupt["r5_seq"] = 999
        self.source.write_bytes(b"".join(self.raw[:2]) + (json.dumps(corrupt) + "\n").encode() + self.raw[3])
        with self.assertRaisesRegex(ValueError, "R6_CONTRACT_MISMATCH"):
            post.consume(self.source, self.db, limit=2)
        self.assertEqual(self.state(), before)

if __name__ == "__main__":
    unittest.main()
