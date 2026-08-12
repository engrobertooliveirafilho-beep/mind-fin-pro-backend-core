from app.mind.p5_6f1_animal_discovery_engine.engine import is_valid_candidate_name

def test_strict_candidate_filter():
    assert is_valid_candidate_name("Bushwacker")
    assert is_valid_candidate_name("Little Yellow Jacket")
    assert not is_valid_candidate_name("auction sale price")
    assert not is_valid_candidate_name("history biography https")
    assert not is_valid_candidate_name("was an American")
