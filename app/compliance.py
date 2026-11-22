"""STEP 520 ComplianceEngine — recovered from Drive, hardened for PAPER-only.

Provenance: Drive original app/compliance.py (file 1ijSuxuIXJFlX8M5KrfMgVgoUQiACQ90-).
The original permitted any unlisted action. This isolated recovery fails closed;
no production route is wired to it. Explicit allowlists cannot authorize real orders.
"""
from typing import Any, Dict


class ComplianceDecision:
    def __init__(self, allowed: bool, reason: str, policy: str = "default"):
        self.allowed = allowed
        self.reason = reason
        self.policy = policy

    def to_dict(self) -> Dict[str, Any]:
        return {"allowed": self.allowed, "reason": self.reason, "policy": self.policy}


class ComplianceEngine:
    """Declarative STEP520 policy with default deny and invariant real-order ban."""

    PAPER_ACTIONS = frozenset({"paper_feedback", "paper_replay", "paper_validate"})

    FORBIDDEN = frozenset({
        "real_order", "live_order", "ftmo_real", "place_order",
        "mt5_real_order", "broker_live_execution",
    })

    def __init__(self, policies: Dict[str, Any] = None):
        self.policies = policies if policies is not None else {
            "default": {
                "allowed_actions": ["paper_feedback", "paper_replay", "paper_validate"],
                "blocked_actions": ["forbidden_example"],
                "reason": "Ação bloqueada pela política padrão STEP 520.",
            }
        }

    def check(self, event: Dict[str, Any]) -> ComplianceDecision:
        if not isinstance(event, dict):
            return ComplianceDecision(False, "Evento inválido.", "safety")
        action = event.get("action")
        if not isinstance(action, str) or not action.strip():
            return ComplianceDecision(False, "Ação ausente ou inválida.", "safety")
        action = action.strip()
        if action not in self.PAPER_ACTIONS:
            return ComplianceDecision(False, "Ação fora do escopo PAPER.", "safety")
        if action in self.FORBIDDEN or action.lower().startswith(("real_", "live_", "ftmo_real")):
            return ComplianceDecision(False, "Execução real proibida.", "safety")
        if event.get("mode") != "PAPER_ONLY" or event.get("real_orders") != "FORBIDDEN" or event.get("ftmo_real") != "FORBIDDEN":
            return ComplianceDecision(False, "Metadados PAPER obrigatórios.", "safety")
        if not isinstance(self.policies, dict):
            return ComplianceDecision(False, "Políticas inválidas.", "safety")
        for policy_name, cfg in self.policies.items():
            if not isinstance(cfg, dict):
                return ComplianceDecision(False, "Política inválida.", str(policy_name))
            blocked = cfg.get("blocked_actions", [])
            allowed = cfg.get("allowed_actions", [])
            if (not isinstance(blocked, (list, tuple, set)) or not isinstance(allowed, (list, tuple, set))
                    or any(not isinstance(x, str) for x in blocked)
                    or any(not isinstance(x, str) for x in allowed)):
                return ComplianceDecision(False, "Lista de ações inválida.", str(policy_name))
            if action in blocked:
                return ComplianceDecision(False, cfg.get("reason", "Ação bloqueada."), str(policy_name))
        for policy_name, cfg in self.policies.items():
            if action in cfg["allowed_actions"]:
                return ComplianceDecision(True, "Ação PAPER permitida.", str(policy_name))
        return ComplianceDecision(False, "Ação não autorizada.", "default")
