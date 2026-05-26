from app.runtime.universal_conversation_authority import build_universal_conversation_context, universal_conversation_reply

def test_p412n_ucca_contract():
    ctx = build_universal_conversation_context("u1", "detalhe melhor", [])
    required = ["sender_id","active_intent","active_reasoning_mode","stage","depth_level","semantic_continuity","grounding_level","execution_need","social_energy","conversational_budget","memory_context"]
    assert all(k in ctx for k in required)

def test_p412n_cross_domain_no_bleed():
    seq = [
        ("u1","Eldora quero melhorar fluidez"),("u1","detalhe melhor"),("u1","aprofunde ainda mais"),("u1","passo a passo"),
        ("u2","pedal CR250R"),("u2","aprofunde"),("u2","detalhe melhor"),
        ("u3","quero validar CAC"),("u3","aprofunde"),
        ("u4","nÃ£o dormi bem hoje"),("u4","detalhe melhor")
    ]
    outs = [universal_conversation_reply(s,m,[]) for s,m in seq]
    banned = ["como posso ajudar","me fale mais","tudo certo por aqui","risk / compatibility","price"]
    assert all(len(o) <= 220 for o in outs)
    assert all(not any(b in o.lower() for b in banned) for o in outs)
    assert "Passo a passo" in outs[3]
    assert "energia baixa" in outs[-1]
