from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def send(body, sender):
    response = client.post(
        "/webhook/whatsapp",
        data={
            "Body": body,
            "From": sender,
        },
    )

    assert response.status_code in (200, 201)
    return response.text.lower()


def assert_valid_contextual_response(response):
    assert response
    assert "webhook_error" not in response
    assert "nameerror" not in response
    assert "traceback" not in response
    assert "<message>" in response
    assert "</message>" in response


def assert_context_was_not_lost(response):
    assert_valid_contextual_response(response)

    context_loss_messages = (
        "sobre qual assunto",
        "qual assunto",
        "qual tópico",
        "qual topico",
        "preciso do tópico",
        "preciso do topico",
        "não tenho contexto",
        "nao tenho contexto",
        "não sei sobre o que",
        "nao sei sobre o que",
    )

    assert not any(
        message in response
        for message in context_loss_messages
    )


def test_p19p29_context_continuity_health_subject():
    sender = "+551111111001"

    first = send(
        "quero emagrecer de forma saudável",
        sender,
    )

    second = send(
        "quais",
        sender,
    )

    third = send(
        "prossiga",
        sender,
    )

    assert_valid_contextual_response(first)
    assert_context_was_not_lost(second)
    assert_context_was_not_lost(third)


def test_p19p29_context_continuity_agriculture_subject():
    sender = "+551111111002"

    first = send(
        "como automatizar confinamento de boi",
        sender,
    )

    second = send(
        "prossiga",
        sender,
    )

    assert_valid_contextual_response(first)
    assert_context_was_not_lost(second)


def test_p19p29_context_continuity_financial_subject():
    sender = "+551111111003"

    first = send(
        "quero validar uma estratégia na FTMO",
        sender,
    )

    second = send(
        "continue",
        sender,
    )

    assert_valid_contextual_response(first)
    assert_context_was_not_lost(second)


def test_p19p29_context_continuity_unrestricted_subject():
    sender = "+551111111005"

    first = send(
        "estou planejando construir uma biblioteca comunitária",
        sender,
    )

    second = send(
        "aprofunde",
        sender,
    )

    third = send(
        "e depois",
        sender,
    )

    assert_valid_contextual_response(first)
    assert_context_was_not_lost(second)
    assert_context_was_not_lost(third)


def test_p19p29_context_continuity_creative_subject():
    sender = "+551111111006"

    first = send(
        "quero criar uma história sobre uma cidade submersa",
        sender,
    )

    second = send(
        "continue",
        sender,
    )

    assert_valid_contextual_response(first)
    assert_context_was_not_lost(second)


def test_p19p29_unknown_followup_requests_context():
    sender = "+551111111004"

    response = send(
        "prossiga",
        sender,
    )

    assert_valid_contextual_response(response)

    clarification_signals = (
        "assunto",
        "tópico",
        "topico",
        "sobre o que",
        "o que você gostaria",
        "o que voce gostaria",
        "o que devo continuar",
    )

    assert any(
        signal in response
        for signal in clarification_signals
    )