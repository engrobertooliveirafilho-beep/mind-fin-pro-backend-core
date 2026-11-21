import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config, validate_ftmo_config
from mind_trader.app.paper.paper_session import PaperTradingSessionManager

class TestFTMOPhaseGate(unittest.TestCase):
    def test_live_phase_rejected(self):
        cfg=default_ftmo_config()
        cfg["phase"]="live"
        self.assertEqual(validate_ftmo_config(cfg)["reason"],"NON_SIMULATION_PHASE_FORBIDDEN")

    def test_real_phase_rejected(self):
        cfg=default_ftmo_config()
        cfg["phase"]="real"
        self.assertFalse(validate_ftmo_config(cfg)["valid"])

    def test_simulation_accepted(self):
        self.assertTrue(validate_ftmo_config(default_ftmo_config())["valid"])

    def test_live_phase_blocks_session_without_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            cfg=default_ftmo_config()
            cfg["phase"]="live"
            (root/"config.json").write_text(json.dumps(cfg))
            manager=PaperTradingSessionManager(str(root/"session.json"),str(root/"ledger.jsonl"),str(root/"config.json"))
            self.assertEqual(manager.open_session()["decision"],"BLOCK_SESSION_INVALID_FTMO_CONFIG")
            self.assertFalse((root/"session.json").exists())

if __name__=="__main__":
    unittest.main()
