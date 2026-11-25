from app.compliance import ComplianceEngine


def test_step520_compliance_allows_normal_action():
    """
    STEP 520 - Garante que ações normais são permitidas.
    """
    engine = ComplianceEngine()
    result = engine.check({"action": "qualquer_coisa"})
    assert result.allowed is True
    assert result.policy == "default"
    assert "permitida" in result.reason.lower()


def test_step520_compliance_blocks_default_forbidden_example():
    """
    STEP 520 - Garante que ação marcada como bloqueada é negada.
    """
    engine = ComplianceEngine()
    result = engine.check({"action": "forbidden_example"})
    assert result.allowed is False
    assert result.policy == "default"
    assert "bloqueada" in result.reason.lower()

