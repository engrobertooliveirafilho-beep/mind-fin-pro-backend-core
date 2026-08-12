import pytest

pytestmark = pytest.mark.skip(reason="P7.4 scaffold only: oversight adapter not built yet")

def test_shadow_mode_does_not_block_runtime():
    assert True

def test_block_decision_is_reported_not_enforced_initially():
    assert True

def test_oversight_does_not_mutate_memory():
    assert True

def test_oversight_does_not_modify_response_without_flag():
    assert True
