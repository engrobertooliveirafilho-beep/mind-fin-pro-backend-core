from anti_rework_engine import assess, digest, run
import json


def record(id='a', capability='memory', data=b'a', tests_passed=True, evidence=None):
    return dict(id=id, capability=capability, sha256=digest(data), commit='abc123', tests_passed=tests_passed, evidence=['pytest'] if evidence is None else evidence)


def test_exact_duplicate_reused():
    assert assess(record('b','other',b'a'), [record()]).status == 'REUSE'


def test_capability_conflict_blocks():
    assert assess(record('b','MEMORY',b'b'), [record()], source_verified=True).reason == 'CAPABILITY_EXISTS_REVIEW_DIFF'


def test_missing_inventory_blocks():
    assert assess(record(), None).status == 'BLOCK'


def test_bad_inventory_blocks():
    assert assess(record(), [{'id': 'x'}]).status == 'BLOCK'


def test_duplicate_ids_block():
    assert assess(record('b','other',b'b'), [record(),record()], source_verified=True).reason == 'INVENTORY_CONFLICT'


def test_unverified_authority_blocks():
    assert assess(record(), []).reason == 'SOURCE_AUTHORITY_UNVERIFIED'


def test_missing_evidence_blocks():
    assert assess(record(evidence=[]), [], source_verified=True).reason == 'TEST_EVIDENCE_MISSING'


def test_failed_test_blocks():
    assert assess(record(tests_passed=False), [], source_verified=True).status == 'BLOCK'


def test_novel_verified_staging_only():
    assert assess(record(), [], source_verified=True).status == 'ALLOW_STAGING'


def test_bad_candidate_blocks():
    assert assess({'capability':'x'}, []).reason == 'CANDIDATE_INCOMPLETE'


def test_missing_file_fail_closed(tmp_path):
    result = run(tmp_path/'missing.json',tmp_path/'inventory.json',tmp_path/'out.json')
    assert result.status == 'BLOCK'
    assert json.loads((tmp_path/'out.json').read_text())['reason'] == 'INPUT_UNREADABLE'
