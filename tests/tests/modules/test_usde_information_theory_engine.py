from app.modules.usde_core.information_theory_engine import InformationTheoryEngine

def test_entropy():
    e=InformationTheoryEngine()
    h=e.entropy([0.5,0.5])
    assert h>0

def test_frequency_entropy():
    events=[
        {"id":1,"values":[1,2]},
        {"id":2,"values":[2,3]},
        {"id":3,"values":[1,3]}
    ]

    r=InformationTheoryEngine().frequency_entropy(events)

    assert r["entropy"]>0

def test_mutual_information():
    mi=InformationTheoryEngine().mutual_information_binary(
        [1,1,0,0],
        [1,1,0,0]
    )

    assert mi>0
