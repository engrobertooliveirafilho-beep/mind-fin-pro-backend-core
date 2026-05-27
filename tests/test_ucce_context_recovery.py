from app.runtime.ucce_shadow_mode import run_ucce_shadow
def test_followup_context():
    a=run_ucce_shadow("u1","problema na implantação","")
    b=run_ucce_shadow("u1","e depois?","")
    assert "problema" in b["reply"].lower() or "continuando" in b["reply"].lower()
def test_social():
    r=run_ucce_shadow("u2","oi","")
    assert r["classification"]=="SOCIAL"
