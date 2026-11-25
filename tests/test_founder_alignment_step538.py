from app.founder_alignment import FounderAlignmentEngine


def test_step538_aligned_plan_with_vision_keywords():
    engine = FounderAlignmentEngine()
    plan = {
        "description": "Expansão segura da MIND FIN PRO com foco em longo prazo e controle de risco.",
        "tags": ["expansao", "longo_prazo", "controle_risco"],
    }
    founder = {
        "vision_keywords": ["longo prazo", "controle de risco", "mind fin pro"],
        "red_lines": ["cassino", "esquema piramide"],
    }
    result = engine.assess(plan, founder)
    assert result.is_aligned is True
    assert result.alignment_score >= 0.6
    assert "viola" not in result.summary.lower()


def test_step538_plan_violating_red_line_is_not_aligned():
    engine = FounderAlignmentEngine()
    plan = {
        "description": "Criar esquema piramide internacional para crescer rapido.",
        "tags": ["crescimento_rapido"],
    }
    founder = {
        "vision_keywords": ["controle de risco"],
        "red_lines": ["esquema piramide", "lavagem de dinheiro"],
    }
    result = engine.assess(plan, founder)
    assert result.is_aligned is False
    assert result.alignment_score < 0.5
    assert any("violates_red_line" in f for f in result.flags)
    assert "viola" in result.summary.lower()

