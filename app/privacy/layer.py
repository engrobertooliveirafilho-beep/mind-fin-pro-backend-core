from typing import Dict, Any, List, Set


class PrivacyByDesignLayer:
    """
    STEP 523 - Camada minima de Privacy-by-Design.

    Nao toca em banco nem em rotas existentes.
    Opera apenas sobre dicionarios em memoria.
    """

    def __init__(self, sensitive_fields: List[str] = None):
        default_fields = ["cpf", "ssn", "account_number", "email"]
        self.sensitive_fields: Set[str] = set(sensitive_fields or default_fields)

    def mask_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica masking em campos sensiveis conhecidos.
        Nao altera o dicionario original.
        """
        masked = dict(record)
        for field in self.sensitive_fields:
            if field in masked and masked[field] is not None:
                masked[field] = "***MASKED***"
        return masked

    def apply_scope(self, record: Dict[str, Any], tenant_id: str, user_id: str) -> Dict[str, Any]:
        """
        Anexa metadados de escopo (tenant/user) ao registro.
        """
        scoped = dict(record)
        scoped["_tenant_id"] = tenant_id
        scoped["_user_id"] = user_id
        return scoped

