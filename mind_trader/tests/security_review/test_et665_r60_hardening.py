"""ET665.R60 security-hardening regression (offline CSV-only synthetic fixtures)."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[2] / 'security' / 'et665_r60_drive_git_reconciliation.py'
SHA = 'a' * 64


def write_csv(path, cols, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)


def scenario(tmp_path, drows=None, grows=None, mapping=None, expected_mapping='correct'):
    d = tmp_path / 'drive.csv'
    g = tmp_path / 'git.csv'
    o = tmp_path / 'out'
    cols = ['path', 'sha256', 'size_bytes']
    write_csv(d, cols, drows if drows is not None else [{'path': 'a', 'sha256': SHA, 'size_bytes': '10'}])
    write_csv(g, cols, grows if grows is not None else [{'path': 'a', 'sha256': SHA, 'size_bytes': '10'}])
    args = [sys.executable, str(SCRIPT), '--git-manifest', str(g), '--drive-manifest', str(d), '--output', str(o),
            '--expected-git-manifest-sha256', hashlib.sha256(g.read_bytes()).hexdigest(),
            '--expected-drive-manifest-sha256', hashlib.sha256(d.read_bytes()).hexdigest()]
    if mapping is not None:
        m = tmp_path / 'mapping.csv'
        write_csv(m, ['drive_path', 'git_path'], mapping)
        args.extend(['--mapping', str(m)])
        if expected_mapping != 'missing':
            expected = hashlib.sha256(m.read_bytes()).hexdigest() if expected_mapping == 'correct' else '0'*64
            args.extend(['--expected-mapping-sha256', expected])
    result = subprocess.run(args, text=True, capture_output=True, timeout=15)
    return result, o


def test_missing_sha256_rejected(tmp_path):
    r, out = scenario(tmp_path, drows=[{'path':'a','sha256':'','size_bytes':'10'}])
    assert r.returncode != 0 and not out.exists()


def test_invalid_size_rejected(tmp_path):
    r, out = scenario(tmp_path, drows=[{'path':'a','sha256':SHA,'size_bytes':'ten'}])
    assert r.returncode != 0 and not out.exists()


def test_negative_size_rejected(tmp_path):
    r, out = scenario(tmp_path, grows=[{'path':'a','sha256':SHA,'size_bytes':'-1'}])
    assert r.returncode != 0 and not out.exists()


def test_mapping_digest_required(tmp_path):
    r, out = scenario(tmp_path, mapping=[{'drive_path':'a','git_path':'a'}], expected_mapping='missing')
    assert r.returncode != 0 and not out.exists()


def test_mapping_digest_mismatch(tmp_path):
    r, out = scenario(tmp_path, mapping=[{'drive_path':'a','git_path':'a'}], expected_mapping='incorrect')
    assert r.returncode != 0 and not out.exists()


def test_valid_mapping_certification_still_false(tmp_path):
    r, out = scenario(tmp_path, mapping=[{'drive_path':'a','git_path':'a'}])
    assert r.returncode == 0
    summary = json.loads((out/'SUMMARY.json').read_text())
    assert summary['full_drive_authority_certified'] is False
    assert summary['semantic_equivalence_certified'] is False
    assert summary['phase_b'] == 'OPEN'


def test_output_path_preexisting_rejected(tmp_path):
    (tmp_path / 'out').mkdir()
    r, out = scenario(tmp_path)
    assert r.returncode != 0
    assert list(out.iterdir()) == []
