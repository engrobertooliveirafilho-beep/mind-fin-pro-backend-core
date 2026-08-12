from app.modules.usde_core.ensemble_evolution_engine import EnsembleEvolutionEngine

def test_weighted_vote():
    r=EnsembleEvolutionEngine().weighted_vote([
        {"score":0.5,"weight":1},
        {"score":0.9,"weight":3}
    ])

    assert r["ensemble_score"]>0.7

def test_evolution():
    r=EnsembleEvolutionEngine().evolve([
        [{"score":0.5,"weight":1}],
        [{"score":0.8,"weight":1}]
    ])

    assert r["best_score"]==0.8
