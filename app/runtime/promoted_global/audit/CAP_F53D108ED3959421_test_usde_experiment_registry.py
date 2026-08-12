from app.modules.usde_core.experiment_registry import ExperimentRegistry

def test_experiment_registry():
    r=ExperimentRegistry()

    e=r.register(
        "markov_validation",
        {"window":100}
    )

    assert "experiment_id" in e
    assert r.count() >= 1
