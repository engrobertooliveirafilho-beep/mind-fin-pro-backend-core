import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.runtime.p2376_de40_big_player_context_xray_engine import sniff


class P2376StreamingCSVTests(unittest.TestCase):
    def test_semicolon_and_comma_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candles.csv"
            for delimiter in (";", ","):
                path.write_text(f"time{delimiter}open{delimiter}high\n" + ("x" * 100000), encoding="utf-8")
                self.assertEqual(sniff(path), delimiter)

    def test_never_uses_full_file_read_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candles.csv"
            path.write_text("time;open;close\n1;2;3\n", encoding="utf-8")
            with patch.object(Path, "read_text", side_effect=AssertionError("full file read")):
                self.assertEqual(sniff(path), ";")


if __name__ == "__main__":
    unittest.main()
