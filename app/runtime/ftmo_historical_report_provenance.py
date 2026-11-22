"""Historical FTMO report provenance; never a current runtime certificate."""
from dataclasses import dataclass

@dataclass(frozen=True)
class FtmoReport:
    version: str
    drive_file_id: str
    historical_reported_tests: int
    individual_case_lines_available: bool
    original_engine_source_verified: bool = False
    current_regression_executed: bool = False
    e2e_certified: bool = False

REPORTS = (
    FtmoReport("V4", "1cPyaAbArZOLzRDY327RZ7tKpSRnBJ-F0", 18, True),
    FtmoReport("V5", "1ADlAYdnxM9Gq6V8pKnwZx9zociYO6yTs", 26, True),
    FtmoReport("V7", "1KhGTBooBrCMDoE_fK69V80zORIJQZGPy", 37, False),
    FtmoReport("V8", "1O2DUlb8Yf6_49aXGn7wN-QTR_lXR6EJo", 37, True),
)

def get_historical_ftmo_reports():
    return REPORTS
