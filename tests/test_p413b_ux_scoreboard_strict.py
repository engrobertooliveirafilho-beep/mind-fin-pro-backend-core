from app.runtime.ux_scoreboard import score_message

def test_strict_penalizes_echo_artificial():
    s=score_message("Aprofunde","Memória contextual: aprofunde Aprofunde mantendo autoridade contextual, mesmo eixo e sem puxar outro domínio.")
    assert s.score < 8.5

def test_strict_penalizes_handback():
    s=score_message("Problemas na implantação","Boa. Isso ajuda bastante. Qual camada você vai mexer agora?")
    assert s.score < 8.5

def test_strict_penalizes_mojibake():
    s=score_message("Tudo bem?","Tudo certo por aqui ­ƒÖé E voc├¬?")
    assert s.score < 8.5
