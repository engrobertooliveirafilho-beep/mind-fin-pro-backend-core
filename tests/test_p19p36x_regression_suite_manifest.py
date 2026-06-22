from app.companionship.regression_suite_manifest import get_regression_suite

def test_regression_manifest_contains_core_layers():
    s=get_regression_suite()
    assert any("p19p36n" in x for x in s)
    assert any("p19p36o" in x for x in s)
    assert any("p19p36p" in x for x in s)
