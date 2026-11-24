"""Focused regressions for the already-published P2614 MT5 loader fix.

PAPER_ONLY: these tests create temporary CSV files only.
"""
import pathlib
import tempfile
import unittest

from app.runtime.p2614_real_fill_replay.loader import load_ohlc


class TestP2614MT5CSV(unittest.TestCase):
    def check_csv(self, data, valid=True, timestamp=None):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = pathlib.Path(directory) / "GER40_m1.csv"
            csv_path.write_text(data, encoding="utf-8")
            if not valid:
                with self.assertRaises(ValueError):
                    load_ohlc(csv_path)
                return
            candles = load_ohlc(csv_path)
            self.assertEqual(len(candles), 1)
            if timestamp:
                self.assertEqual(candles[0]["time"].isoformat(), timestamp)

    def test_mt5_tab_separate_date_time(self):
        self.check_csv(
            "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n"
            "2026.11.24\t09:30:00\t1.1\t1.2\t1.0\t1.15\n",
            timestamp="2026-11-24T09:30:00",
        )

    def test_semicolon_delimiter_and_decimal_comma(self):
        self.check_csv(
            "date;time;open;high;low;close\n"
            "2026-11-24;09:30:00;1,10;1,20;1,00;1,15\n",
            timestamp="2026-11-24T09:30:00",
        )

    def test_semicolon_delimiter_and_decimal_dot(self):
        self.check_csv(
            "date;time;open;high;low;close\n"
            "2026-11-24;09:30:00;1.10;1.20;1.00;1.15\n",
            timestamp="2026-11-24T09:30:00",
        )

    def test_header_only_fails_closed(self):
        self.check_csv("date,time,open,high,low,close\n", valid=False)

    def test_zero_bytes_fails_closed(self):
        self.check_csv("", valid=False)

    def test_duplicate_header_fails_closed(self):
        self.check_csv(
            "date,time,open,high,low,close,open\n"
            "2026-11-24,09:30:00,1,2,1,1.5,1\n",
            valid=False,
        )

    def test_incomplete_csv_row_fails_closed(self):
        self.check_csv(
            "date,time,open,high,low,close\n"
            "2026-11-24,09:30:00,1,2\n",
            valid=False,
        )

    def test_malformed_timestamp_fails_closed(self):
        self.check_csv(
            "date,time,open,high,low,close\n"
            "2026-11-24,invalid,1,2,1,1.5\n",
            valid=False,
        )


if __name__ == "__main__":
    unittest.main()
