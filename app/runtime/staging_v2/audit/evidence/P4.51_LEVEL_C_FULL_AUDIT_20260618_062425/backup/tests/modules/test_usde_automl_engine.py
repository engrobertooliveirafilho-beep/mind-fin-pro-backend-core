from app.modules.usde_core.automl_engine import AutoMLEngine

def test_automl_search():
    r=AutoMLEngine().search()

    assert r["best_model"]=="XGBoost"

def test_automl_candidates():
    r=AutoMLEngine().evaluate_candidates([
        {"name":"A","score":0.5},
        {"name":"B","score":0.9}
    ])

    assert r["best_model"]=="B"
