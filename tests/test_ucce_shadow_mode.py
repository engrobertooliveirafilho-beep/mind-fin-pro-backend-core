from app.runtime.ucce_shadow_mode import run_ucce_shadow
from app.runtime.ucce_decision_diff import compare_decisions

def test_ucce_shadow_safe():
    live="Tudo bem"
    out=run_ucce_shadow("u1","oi",live)
    diff=compare_decisions(live,out)
    assert isinstance(out,dict)
    assert diff["winner"] in ["dispatcher","ucce"]
    assert out["classification"]=="SOCIAL"
