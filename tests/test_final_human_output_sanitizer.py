
from app.runtime.final_human_output_sanitizer import sanitize_final_human_output

def test_blocks_robotic_labeled_templates():
    out = sanitize_final_human_output("Detalhamento: algo. Pontos-chave: 1) causa")
    assert "Detalhamento:" not in out
    assert "Pontos-chave:" not in out

def test_preserves_normal_answer():
    assert sanitize_final_human_output("Resultado: 24.") == "Resultado: 24."
