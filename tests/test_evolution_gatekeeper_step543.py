from app.evolution_gatekeeper import EvolutionGatekeeper


def test_step543_low_risk_high_alignment_low_redundancy_is_approved():
    gate = EvolutionGatekeeper()
    proposal = {
        "step_id": 600,
        "title": "Novo modulo de otimizacao prudente",
        "risk_score": 0.3,
        "alignment_score": 0.8,
        "redundancy_score": 0.2,
    }
    decision = gate.evaluate(proposal)
    assert decision.approved_for_human_review is True
    assert any("elegivel" in r.lower() for r in decision.reasons)


def test_step543_high_risk_or_low_alignment_is_rejected():
    gate = EvolutionGatekeeper()
    # alto risco
    proposal1 = {
        "step_id": 601,
        "title": "Coisa muito agressiva",
        "risk_score": 0.9,
        "alignment_score": 0.9,
        "redundancy_score": 0.1,
    }
    d1 = gate.evaluate(proposal1)
    assert d1.approved_for_human_review is False
    assert any("risco alto" in r.lower() for r in d1.reasons)

    # baixo alinhamento
    proposal2 = {
        "step_id": 602,
        "title": "Coisa desalinhada",
        "risk_score": 0.2,
        "alignment_score": 0.3,
        "redundancy_score": 0.1,
    }
    d2 = gate.evaluate(proposal2)
    assert d2.approved_for_human_review is False
    assert any("alinhamento insuficiente" in r.lower() for r in d2.reasons)

