from app.rsigc.self_audit.audit import SelfAuditEngine
from app.rsigc.architecture_validator.validator import ArchitectureValidator
from app.rsigc.conflict_resolver.resolver import ConflictResolver
from app.rsigc.improvement_loop.loop import RecursiveImprovementLoop

class RSIGC:
    def __init__(self):
        self.audit = SelfAuditEngine()
        self.validator = ArchitectureValidator()
        self.resolver = ConflictResolver()
        self.loop = RecursiveImprovementLoop()

    def run_governance_cycle(self, system_state):
        report = self.audit.audit(system_state)
        validation = self.validator.validate(system_state)
        resolution = self.resolver.resolve(system_state)
        improvement = self.loop.improve(report)

        return {
            "audit": report,
            "validation": validation,
            "resolution": resolution,
            "improvement": improvement
        }
