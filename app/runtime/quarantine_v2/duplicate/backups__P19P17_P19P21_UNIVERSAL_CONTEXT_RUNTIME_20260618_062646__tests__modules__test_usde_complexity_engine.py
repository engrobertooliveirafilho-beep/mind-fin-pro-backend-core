from app.modules.usde_core.complexity_engine import ComplexityEngine

def test_kolmogorov_proxy():
    r=ComplexityEngine().kolmogorov_proxy(
        "aaaaaaaaaaaaaaaaaaaaaaaaaa"
    )

    assert r["complexity_ratio"]>0

def test_lz_complexity():
    r=ComplexityEngine().lempel_ziv_complexity(
        [1,2,3,1,2,3]
    )

    assert r["lz_complexity"]>0

def test_mdl_score():
    r=ComplexityEngine().mdl_score(
        100,
        200
    )

    assert r["mdl"]==300
