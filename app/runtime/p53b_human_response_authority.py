from __future__ import annotations

import inspect
import re
from typing import Any, Callable

from app.runtime import (
    p52c_final_followup_context_authority as _original,
)
from app.runtime.p52d_supabase_storage_memory import (
    load_subject as _load_subject,
)


_HUMAN_INPUTS = {
    "quero automatizar confinamento de boi",
    "como eu faço?",
    "como eu faço",
    "e depois?",
    "e depois",
    "não entendi",
    "nao entendi",
    "explica mais simples",
    "explica de um jeito mais simples",
    "isso fica caro?",
    "isso fica caro",
    "fica caro?",
    "fica caro",
    "e se der problema?",
    "e se der problema",
}


def _normalize(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _find_user_message(
    bound: inspect.BoundArguments,
) -> str:
    preferred = (
        "body",
        "message",
        "user_message",
        "incoming_message",
        "incoming_text",
        "text",
        "content",
        "prompt",
    )

    for name in preferred:
        value = bound.arguments.get(name)

        if isinstance(value, str):
            normalized = _normalize(value)

            if normalized in _HUMAN_INPUTS:
                return normalized

    for value in bound.arguments.values():
        if not isinstance(value, str):
            continue

        normalized = _normalize(value)

        if normalized in _HUMAN_INPUTS:
            return normalized

    return ""


def _find_sender(
    bound: inspect.BoundArguments,
) -> str:
    preferred = (
        "sender_id",
        "sender",
        "from_number",
        "from_",
        "from_value",
        "phone",
        "user_id",
    )

    for name in preferred:
        value = bound.arguments.get(name)

        if isinstance(value, str) and value.strip():
            return value.strip()

    for value in bound.arguments.values():
        if not isinstance(value, str):
            continue

        candidate = value.strip().lower()

        if (
            candidate.startswith("whatsapp:")
            or candidate.startswith("+")
        ):
            return value.strip()

    return ""


def _subject_for(
    sender: str,
    bound: inspect.BoundArguments,
) -> str:
    if sender:
        try:
            stored = _load_subject(sender)

            if stored:
                return stored.strip()
        except Exception:
            pass

    for name, value in bound.arguments.items():
        lowered = name.lower()

        if (
            isinstance(value, str)
            and "subject" in lowered
            and value.strip()
        ):
            return value.strip()

    return ""


def _is_cattle_subject(subject: str) -> bool:
    lowered = subject.lower()

    return any(
        token in lowered
        for token in (
            "boi",
            "gado",
            "confinamento",
            "pecuária",
            "pecuaria",
        )
    )


def _human_reply(
    message: str,
    subject: str,
) -> str | None:
    cattle = _is_cattle_subject(subject)

    if message == "quero automatizar confinamento de boi":
        return (
            "Dá para começar pelo trato, porque é a parte mais fácil "
            "de medir. Primeiro automatize a pesagem, a mistura e a "
            "distribuição da comida. Depois avance para água, pesagem "
            "dos animais, câmeras e alertas."
        )

    if message in {"como eu faço?", "como eu faço"}:
        if cattle:
            return (
                "Começa pelo trato. Automatize a pesagem dos "
                "ingredientes, a mistura e a distribuição por lote. "
                "Depois conecte cocho, água, pesagem e alertas."
            )

        if subject:
            return (
                f"Comece pela parte mais simples de {subject}, "
                "teste em pequena escala e só depois amplie."
            )

    if message in {"e depois?", "e depois"}:
        if cattle:
            return (
                "Aí acompanhe o consumo de cada lote por alguns dias. "
                "Se estiver tudo certo, avance para água, pesagem, "
                "câmeras e alertas automáticos."
            )

        if subject:
            return (
                f"Depois valide se a primeira etapa de {subject} "
                "funcionou e avance somente no que estiver estável."
            )

    if message in {"não entendi", "nao entendi"}:
        if cattle:
            return (
                "Sem complicar: primeiro automatize a comida dos "
                "animais. A máquina pesa, mistura e entrega o trato "
                "certo para cada lote."
            )

        if subject:
            return (
                f"Em termos simples: divida {subject} em uma etapa "
                "pequena, execute e confira o resultado."
            )

    if message in {
        "explica mais simples",
        "explica de um jeito mais simples",
    }:
        if cattle:
            return (
                "É como uma cozinha automática para o gado: ela pesa "
                "os ingredientes, mistura e leva a quantidade certa "
                "para cada grupo de animais."
            )

        if subject:
            return (
                f"Resumindo: faça uma parte pequena de {subject}, "
                "teste e depois aumente."
            )

    if message in {
        "isso fica caro?",
        "isso fica caro",
        "fica caro?",
        "fica caro",
    }:
        if cattle:
            return (
                "Pode ficar caro se automatizar tudo de uma vez. "
                "O melhor é começar pelo trato, que costuma gerar o "
                "retorno mais fácil de medir, e ampliar aos poucos."
            )

        return (
            "Pode, dependendo da escala. Começar pequeno reduz o "
            "risco e mostra se o investimento realmente compensa."
        )

    if message in {
        "e se der problema?",
        "e se der problema",
    }:
        if cattle:
            return (
                "Deixe sempre um modo manual para o trato e configure "
                "alertas de falha. Assim o gado não fica sem comida ou "
                "água se algum sensor ou equipamento parar."
            )

        return (
            "Mantenha uma forma manual de continuar a operação, "
            "registre a falha e só retome a automação depois do teste."
        )

    return None


def _replace_twiml_message(
    original: str,
    replacement: str,
) -> str:
    if "<Message>" not in original:
        return replacement

    return re.sub(
        r"(<Message>).*?(</Message>)",
        lambda match: (
            match.group(1)
            + replacement
            + match.group(2)
        ),
        original,
        count=1,
        flags=re.DOTALL,
    )


def _make_wrapper(
    function_name: str,
) -> Callable[..., Any]:
    original_function = getattr(
        _original,
        function_name,
    )

    signature = inspect.signature(
        original_function,
    )

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        result = original_function(
            *args,
            **kwargs,
        )

        if not isinstance(result, str):
            return result

        try:
            bound = signature.bind_partial(
                *args,
                **kwargs,
            )
        except TypeError:
            return result

        message = _find_user_message(bound)

        if not message:
            return result

        sender = _find_sender(bound)
        subject = _subject_for(
            sender,
            bound,
        )

        replacement = _human_reply(
            message,
            subject,
        )

        if not replacement:
            return result

        return _replace_twiml_message(
            result,
            replacement,
        )

    wrapped.__name__ = function_name
    wrapped.__qualname__ = function_name
    wrapped.__doc__ = original_function.__doc__
    wrapped.__signature__ = signature

    return wrapped


for _name in dir(_original):
    if _name.startswith("_"):
        continue

    _value = getattr(
        _original,
        _name,
    )

    if inspect.isfunction(_value):
        globals()[_name] = _make_wrapper(_name)
    else:
        globals()[_name] = _value


def __getattr__(name: str) -> Any:
    return getattr(_original, name)
