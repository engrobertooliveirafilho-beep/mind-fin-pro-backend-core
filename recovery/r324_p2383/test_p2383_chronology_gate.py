from pathlib import Path
import pytest
from p2383_chronology_gate import certify, inspect

ORIGINAL = Path(__file__).with_name('historical_p2383_windows.csv')

def test_original_is_rejected_without_mutation():
    before = ORIGINAL.read_bytes()
    issues = inspect(ORIGINAL)
    for window in (1, 3, 5):
        assert any(f'window {window}: start after end' in issue for issue in issues)
    with pytest.raises(ValueError, match='P2383_CHRONOLOGY_BLOCKED'):
        certify(ORIGINAL)
    assert ORIGINAL.read_bytes() == before

def test_valid_chronological_fixture_passes(tmp_path):
    path = tmp_path / 'windows.csv'
    path.write_text('window_id,start_time,end_time\n1,2025.01.01 00:00:00,2025.02.01 00:00:00\n2,2025.02.02 00:00:00,2025.03.01 00:00:00\n')
    assert certify(path) is True

def test_overlap_rejected(tmp_path):
    path = tmp_path / 'windows.csv'
    path.write_text('window_id,start_time,end_time\n1,2025.01.01 00:00:00,2025.02.01 00:00:00\n2,2025.01.15 00:00:00,2025.03.01 00:00:00\n')
    assert any('not strictly after' in issue for issue in inspect(path))
