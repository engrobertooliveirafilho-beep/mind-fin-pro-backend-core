"""ET665.R386: adversarial regression for the integrated 19-agent chain.

No production routing, real broker calls, or promotion. Each mutation must
fail closed rather than silently produce a PASS report.
"""
from unittest.mock import patch
from mind_trader.experimental import et665_r384_integrated_evidence as integrated

def check_adversarial():
    baseline=integrated.build()
    if baseline["candidate_executed"]!=19 or baseline["phase_b_certified"]!=0:
        raise RuntimeError("unsafe baseline")
    cases={}
    original_run=integrated.run
    def mutate_chain():
        report=original_run()
        report["candidate_chain_sha256"]="0"*64
        report["candidate_outputs"][0]["output_sha256"]="0"*64
        return report
    with patch.object(integrated,"run",side_effect=mutate_chain):
        try:integrated.build()
        except RuntimeError:cases["corrupted_agent_hash"]="REJECTED"
        else:raise RuntimeError("corrupted agent hash accepted")
    def drop_agent():
        report=original_run()
        report["candidate_outputs"].pop()
        return report
    with patch.object(integrated,"run",side_effect=drop_agent):
        try:integrated.build()
        except RuntimeError:cases["missing_agent"]="REJECTED"
        else:raise RuntimeError("missing agent accepted")
    def falsify_count():
        report=original_run()
        report["candidate_executed"]=18
        return report
    with patch.object(integrated,"run",side_effect=falsify_count):
        try:integrated.build()
        except RuntimeError:cases["false_agent_count"]="REJECTED"
        else:raise RuntimeError("false count accepted")
    return {"status":"ADVERSARIAL_REJECTIONS_PASS","cases":cases,
            "official_hp19_certified":0,"phase_b_certified":0,
            "real_orders":"FORBIDDEN"}
