import unittest
from app.runtime.ftmo_historical_report_provenance import get_historical_ftmo_reports

class HistoricalReportProvenanceTests(unittest.TestCase):
    def test_versions_and_counts(self):
        self.assertEqual([(x.version,x.historical_reported_tests) for x in get_historical_ftmo_reports()],
                         [('V4',18),('V5',26),('V7',37),('V8',37)])
    def test_all_have_drive_evidence(self):
        self.assertTrue(all(x.drive_file_id for x in get_historical_ftmo_reports()))
    def test_v7_is_summary_only(self):
        self.assertFalse(next(x for x in get_historical_ftmo_reports() if x.version=='V7').individual_case_lines_available)
    def test_no_source_or_runtime_certification(self):
        self.assertTrue(all(not x.original_engine_source_verified and not x.current_regression_executed and not x.e2e_certified
                            for x in get_historical_ftmo_reports()))
