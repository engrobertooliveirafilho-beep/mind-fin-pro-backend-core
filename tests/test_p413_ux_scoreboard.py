from app.runtime.ux_scoreboard import score_message, score_batch

def test_score_good_reply():
    s = score_message("Quanto é 4x6", "Resultado: 24.")
    assert s.score >= 8.5
    assert s.leak == 0
    assert s.fallback == 0

def test_score_leak_penalty():
    s = score_message("Busque o erro", "Resumo técnico do MIND/Eldora: Runtime estável V2 ativo.")
    assert s.leak == 1
    assert s.score < 8.5

def test_batch_pass():
    out = score_batch([
        {"message":"Oi","reply":"Oi, Roberto. Tudo certo?"},
        {"message":"Quanto é 4x6","reply":"Resultado: 24."},
    ])
    assert out["passed"] is True
