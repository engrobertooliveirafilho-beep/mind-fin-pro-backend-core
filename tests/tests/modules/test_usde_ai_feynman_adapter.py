from app.modules.usde_core.ai_feynman_adapter import AIFeynmanAdapter

def test_dimensional_consistency():
    r=AIFeynmanAdapter().dimensional_consistency(
        {"x":"m","y":"m"}
    )

    assert r["consistent"] is True

def test_candidate_equations():
    r=AIFeynmanAdapter().candidate_equations(
        [1,2,3],
        [2,4,6]
    )

    assert len(r)>0

def test_rank():
    r=AIFeynmanAdapter().rank(
        [{"equation":"y=2*x"}]
    )

    assert r["best_equation"]=="y=2*x"
