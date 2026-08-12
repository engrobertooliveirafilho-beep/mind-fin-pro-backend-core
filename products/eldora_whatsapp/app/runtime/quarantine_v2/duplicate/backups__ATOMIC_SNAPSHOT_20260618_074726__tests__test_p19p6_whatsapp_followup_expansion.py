from app.api.whatsapp import _p19p6_expand_bad_followup_template

def test_p19p6_blocks_contextual_template_leak():
    out = _p19p6_expand_bad_followup_template(
        "aprofunde",
        "Execução contextual: continua do ponto anterior com evidência e próximo passo."
    )
    assert "execução contextual" not in out.lower()
    assert "continua do ponto anterior" not in out.lower()
    assert "confinamento" in out.lower()
    assert "trato" in out.lower()
    assert len(out) > 250
