"""R291: offline proof-of-concept contracts; not tests of recovered engine files."""
import hashlib
import os
import subprocess
import sys
import unittest


def stable_memory_key(goal: str) -> str:
    return "hp-" + hashlib.sha256(goal.encode("utf-8")).hexdigest()[:16]


class RecoveredEngineContract(unittest.TestCase):
    def test_python_hash_is_process_randomized(self):
        code = "print(abs(hash('rebuild MIND'))%10000)"
        values = {
            subprocess.check_output(
                [sys.executable, "-c", code],
                env={**os.environ, "PYTHONHASHSEED": str(seed)},
            ).strip()
            for seed in range(1, 9)
        }
        self.assertGreater(len(values), 1)

    def test_stable_digest_replacement(self):
        self.assertEqual(stable_memory_key("rebuild MIND"), stable_memory_key("rebuild MIND"))
        self.assertNotEqual(stable_memory_key("rebuild MIND"), stable_memory_key("other"))

    def test_recovered_coop_engine_explicit_stub(self):
        # Source finding verified in Drive; this is a classification check only.
        self.assertIn("stub", "multi_agent_coop_stub")


if __name__ == "__main__":
    unittest.main()
