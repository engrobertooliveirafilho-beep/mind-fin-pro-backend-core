from app.runtime.final_human_output_sanitizer import sanitize_final_human_output

def test_empty_does_not_emit_generic_fallback():
    assert "vamos seguir pelo ponto real" not in sanitize_final_human_output("").lower()

def test_robotic_label_is_stripped_without_generic_fallback():
    out = sanitize_final_human_output("Diagnóstico: erro no webhook")
    assert out == "erro no webhook"

def test_generic_point_real_is_blocked():
    out = sanitize_final_human_output("Vamos seguir pelo ponto real e validar o próximo passo.")
    assert "vamos seguir pelo ponto real" not in out.lower()

def test_identity_question_not_overwritten():
    out = sanitize_final_human_output("quem é vc?")
    assert out == "quem é vc?"

def test_calculation_not_overwritten():
    out = sanitize_final_human_output("Resultado: 24.")
    assert out == "Resultado: 24."
