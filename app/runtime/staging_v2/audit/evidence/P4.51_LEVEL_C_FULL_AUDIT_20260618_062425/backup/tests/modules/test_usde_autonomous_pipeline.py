from app.modules.usde_core.autonomous_scientific_pipeline import AutonomousScientificPipeline

def test_autonomous_pipeline():
    r=AutonomousScientificPipeline().run(
        {"events":1000}
    )

    assert r["generated"] > 0
    assert r["executed"] == 5
