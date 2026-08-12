from app.modules.usde_core.symbolic_regression_engine import SymbolicRegressionEngine

def test_symbolic_regression_fit():
    r=SymbolicRegressionEngine().fit_linear(
        [1,2,3,4],
        [2,4,6,8]
    )

    assert r["r2"] > 0.99

def test_symbolic_regression_discover():
    r=SymbolicRegressionEngine().discover(
        [1,2,3,4],
        [2,4,6,8]
    )

    assert r["best_model"]=="linear"
