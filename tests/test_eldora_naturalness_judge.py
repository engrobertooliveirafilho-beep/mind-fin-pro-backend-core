from app.humanization.humanization_runtime import humanization_runtime
def test_no_identity_fallback():
    r=humanization_runtime("oi","Sou a Eldora")
    assert "sou a eldora" not in r["answer"].lower()
def test_because_context():
    r=humanization_runtime("porque?","ok")
    assert "porque" in r["answer"].lower() or "causalidade" in r["answer"].lower()
def test_preserve_technical():
    r=humanization_runtime("me explica derivada","Derivada mede taxa de mudança")
    assert "derivada" in r["answer"].lower()
def test_followup():
    r=humanization_runtime("acho q vou desistir","ok")
    assert "fala" in r["answer"].lower() or "travou" in r["answer"].lower()
def test_score():
    r=humanization_runtime("boa tarde","ok")
    assert r["judge"]["humanization_score"]>=99.9
def test_multi():
    r=humanization_runtime("boa tarde","Boa tarde Roberto. Melhorou bastante. Ainda tem um ponto travando.")
    assert len(r["messages"])<=5
