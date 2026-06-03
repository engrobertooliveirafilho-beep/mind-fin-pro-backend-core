
from app.runtime.text_provider_adapters import build_context_prompt

def test_context_prompt_contains_subject_and_domain():
    x=build_context_prompt(
        "quanto ela faz por litro?",
        {
            "last_subject":"RAM 2500 ano 2026",
            "last_domain":"vehicle_buying"
        }
    )
    assert "RAM 2500" in x
    assert "vehicle_buying" in x
    assert "quanto ela faz por litro?" in x

def test_context_prompt_passthrough_without_context():
    x=build_context_prompt("teste",{})
    assert x=="teste"
