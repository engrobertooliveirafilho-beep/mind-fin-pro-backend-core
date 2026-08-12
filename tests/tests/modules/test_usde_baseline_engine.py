from app.modules.usde_core.baseline_engine import BaselineEngine

def test_uniform_baseline():
    r=BaselineEngine().uniform_baseline(25,15)
    assert r["expected_hit_rate"]>0

def test_frequency_baseline():
    freq={
        "1":{"frequency":0.9},
        "2":{"frequency":0.8},
        "3":{"frequency":0.1}
    }
    r=BaselineEngine().frequency_baseline(freq,2)
    assert r["prediction"]==[1,2]
