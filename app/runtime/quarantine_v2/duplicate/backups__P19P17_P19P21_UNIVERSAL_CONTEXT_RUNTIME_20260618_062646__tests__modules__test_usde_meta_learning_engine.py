from app.modules.usde_core.meta_learning_engine import MetaLearningEngine

def test_meta_rank():
    r=MetaLearningEngine().rank_experiments([
        {"score":0.5},
        {"score":0.9}
    ])

    assert r["best"]["score"]==0.9

def test_meta_learn():
    r=MetaLearningEngine().learn([
        {"strategy":"A","score":0.5},
        {"strategy":"A","score":0.6},
        {"strategy":"B","score":0.9}
    ])

    assert r["recommended_strategy"]=="B"
