from app.scg.permissions.boundary import PermissionBoundary
from app.scg.privacy.third_party import ThirdPartyProtection
from app.scg.sensitivity.filter import SensitivityFilter
from app.scg.ethics.gate import EthicsGate

class SCG:
    def __init__(self):
        self.permission = PermissionBoundary()
        self.privacy = ThirdPartyProtection()
        self.sensitivity = SensitivityFilter()
        self.ethics = EthicsGate()

    def validate(self, input_source, data):
        p = self.permission.validate(input_source)
        t = self.privacy.filter(data)
        s = self.sensitivity.scan(data)
        e = self.ethics.enforce(data)

        return {
            "permission_ok": p,
            "privacy_ok": t,
            "sensitivity_ok": s,
            "ethics_ok": e,
            "approved": p and t["analysis_allowed"] and s["allowed"]
        }
