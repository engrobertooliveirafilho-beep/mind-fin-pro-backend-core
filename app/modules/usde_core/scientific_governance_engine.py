from __future__ import annotations

class ScientificGovernanceEngine:
    def validate_release(self, metrics:dict)->dict:
        blockers=[]

        if metrics.get("tests_passed",0) <= 0:
            blockers.append("NO_TESTS")

        if metrics.get("baseline_validated",False) is False:
            blockers.append("BASELINE_NOT_VALIDATED")

        if metrics.get("red_team_passed",False) is False:
            blockers.append("RED_TEAM_NOT_PASSED")

        if metrics.get("walk_forward_validated",False) is False:
            blockers.append("WALK_FORWARD_NOT_VALIDATED")

        return {
            "approved":len(blockers)==0,
            "blockers":blockers,
            "governance_status":"APPROVED" if len(blockers)==0 else "BLOCKED"
        }

    def audit_model(self, model:dict)->dict:
        risk=0

        if model.get("accuracy",0) > 0.95:
            risk += 3

        if model.get("overfitting",0) > 0.40:
            risk += 3

        if model.get("baseline_gain",0) <= 0:
            risk += 2

        return {
            "risk_score":risk,
            "risk_level":"HIGH" if risk>=5 else "MEDIUM" if risk>=3 else "LOW"
        }
