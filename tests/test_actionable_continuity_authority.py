
from app.runtime.actionable_continuity_authority import resolve_actionable_followup, guard_actionable_reply

FORBIDDEN = [
    "Memória contextual",
    "vou manter a continuidade",
    "Pode mandar a dúvida direto",
    "Entendi. Vou tratar isso como tarefa",
    "sem puxar contexto antigo",
    "responder pelo que você acabou de falar",
]

def clean(out):
    for f in FORBIDDEN:
        assert f.lower() not in out.lower()

def test_calculate_20_plus_30():
    out = resolve_actionable_followup("u", "calcule 20 mais 30", {})
    clean(out)
    assert "50" in out

def test_detail_uses_last_context():
    out = resolve_actionable_followup("u", "consegue detalhar mais?", {"active_topic": "implantações", "last_open_task": "validar Render"})
    clean(out)
    assert "validar Render" in out or "implantações" in out

def test_continue_uses_previous_line():
    out = resolve_actionable_followup("u", "e depois?", {"active_topic": "P4.12N-C", "last_open_task": "rodar live E2E"})
    clean(out)
    assert "rodar live E2E" in out or "P4.12N-C" in out

def test_guard_blocks_placeholder():
    out = guard_actionable_reply("Memória contextual: aprofunde...", "u", "consegue detalhar mais?", {"active_topic": "continuidade"})
    clean(out)
    assert "Detalhamento" in out

def test_verify_generates_checklist():
    out = resolve_actionable_followup("u", "verifique esse problema", {"active_topic": "webhook"})
    clean(out)
    assert "Verificação" in out

def test_analyze_generates_analysis():
    out = resolve_actionable_followup("u", "analise esse contrato", {"active_topic": "contrato"})
    clean(out)
    assert "Análise" in out
