import csv
from pathlib import Path
import pytest
from p2383_chronology_gate import certify, inspect

ORIGINAL = Path('/mnt/data/de40_walk_forward_windows.csv')

def test_original_is_rejected_without_mutation():
    before = ORIGINAL.read_bytes()
    issues = inspect(ORIGINAL)
    assert any('window 1: start after end' in x for x in issues)
    assert any('window 3: start after end' in x for x in issues)
    assert any('window 5: start after end' in x for x in issues)
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
    assert any('not strictly after' in x for x in inspect(path))
