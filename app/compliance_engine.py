from typing import Dict, Any


class ComplianceDecision:
    """
    Representa o resultado da checagem de compliance.

    STEP 520: estrutura mínima, mas já rastreável.
    """

    def __init__(self, allowed: bool, reason: str, policy: str = "default"):
        self.allowed = allowed
        self.reason = reason
        self.policy = policy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "policy": self.policy,
        }


class ComplianceEngine:
    """
    STEP 520 - Núcleo inicial do Compliance Engine.

    - 100% isolado (não intercepta rotas existentes).
    - Usa políticas declarativas simples.
    - Retorna sempre um ComplianceDecision rastreável.
    """

    def __init__(self, policies: Dict[str, Any] = None):
        # Políticas declarativas mínimas.
        # Futuramente podem ser carregadas de banco/config.
        self.policies = policies or {
            "default": {
                "blocked_actions": ["forbidden_example"],
                "reason": "Ação bloqueada pela política padrão STEP 520.",
            }
        }

    def check(self, event: Dict[str, Any]) -> ComplianceDecision:
        """
        Checagem mínima e segura de compliance.

        :param event: dicionário com pelo menos uma chave "action".
        :return: ComplianceDecision com allowed True/False, motivo e policy.
        """
        action = event.get("action")
        if not isinstance(action, str) or not action.strip():
            return ComplianceDecision(False, "Ação não identificada.", "default")

        for policy_name, cfg in self.policies.items():
            blocked = cfg.get("blocked_actions", [])
            if action in blocked:
                return ComplianceDecision(
                    allowed=False,
                    reason=cfg.get("reason", "Violação de política."),
                    policy=policy_name,
                )

        # Caso não haja política que bloqueie explicitamente, permitir.
        return ComplianceDecision(
            allowed=True,
            reason="Ação permitida pela política padrão STEP 520.",
            policy="default",
        )

