from app.eldora.canonical_registry import CANONICAL_FUNCTIONS, STATUS_FINAL_ADICIONAL

def test_registry_status():
    assert STATUS_FINAL_ADICIONAL == "ELDORA_CANONICAL_FUNCTIONS_EXPANDED"

def test_all_families_present():
    assert len(CANONICAL_FUNCTIONS) >= 11

def test_lotofacil_isolated():
    funcs = CANONICAL_FUNCTIONS["skills_study_lotofacil"]
    assert "lotofacil_report" in funcs

def test_lgpd_present():
    assert "delete_user_data" in CANONICAL_FUNCTIONS["identity"]
