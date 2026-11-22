"""Regression for Trader1 exporter config preflight (not an MQL5 runtime test)."""
import unittest
from app.runtime.trader1_exporter_config_gate import ExporterConfig, validate_exporter_config

class Trader1ExporterConfig(unittest.TestCase):
    def test_original_defaults(self):
        self.assertEqual(validate_exporter_config(ExporterConfig(31,500,0)).window_days,31)

    def test_zero_window_rejected(self):
        with self.assertRaises(ValueError): validate_exporter_config(ExporterConfig(0,500,0))

    def test_negative_window_rejected(self):
        with self.assertRaises(ValueError): validate_exporter_config(ExporterConfig(-1,500,0))

    def test_excessive_window_rejected(self):
        with self.assertRaises(ValueError): validate_exporter_config(ExporterConfig(366,500,0))

    def test_minimum_bars_rejected(self):
        with self.assertRaises(ValueError): validate_exporter_config(ExporterConfig(31,0,0))

    def test_maximum_below_minimum_rejected(self):
        with self.assertRaises(ValueError): validate_exporter_config(ExporterConfig(31,500,499))

    def test_bool_rejected(self):
        with self.assertRaises(ValueError): validate_exporter_config(ExporterConfig(True,500,0))

    def test_valid_bounded_export(self):
        self.assertEqual(validate_exporter_config(ExporterConfig(7,100,200)).maximum_bars,200)

if __name__ == "__main__":
    unittest.main()
