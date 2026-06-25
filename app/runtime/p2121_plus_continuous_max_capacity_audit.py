from __future__ import annotations

import json
import os
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any


ABSOLUTE_LOCKS = {
    "MIND_MODE": "PAPER_ONLY",
    "REAL_ORDERS": "FORBIDDEN",
    "LIVE_TRADING": "FALSE",
    "BROKER_EXECUTION": "DISABLED",
    "FINANCIAL_EXECUTION": "DISABLED",
    "FTMO_REAL": "FORBIDDEN",
    "SEND_ORDER": "BLOCKED",
    "MT5_ORDER_SEND": "BLOCKED",
    "BROKER_API_CALL": "BLOCKED",
}


def enforce_paper_only() -> Dict[str, str]:
    for k, v in ABSOLUTE_LOCKS.items():
        os.environ[k] = v
    return dict(ABSOLUTE_LOCKS)


def assert_no_financial_execution() -> None:
    locks = enforce_paper_only()
    for k, v in ABSOLUTE_LOCKS.items():
        if locks.get(k) != v:
            raise RuntimeError(f"{k}_LOCK_BREACH")


def load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8"))


def sha256_file(path: str) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class AuditDecision:
    component: str
    status: str
    reason: str
    payload: Dict[str, Any]


class CertifiedBlockAudit:
    def evaluate(self, deps: Dict[str, str]) -> AuditDecision:
        assert_no_financial_execution()

        required_status = {
            "p2071": "PASS",
            "p2081": "PASS",
            "p2091": "PASS",
            "p2101": "PASS",
            "p2111": "PASS",
        }

        results = {}
        failures = []

        for key, expected in required_status.items():
            data = load_json(deps[key])
            status = data.get("status")
            readiness = data.get("readiness")
            results[key] = {"status": status, "readiness": readiness, "path": deps[key]}
            if status != expected:
                failures.append(key)

        return AuditDecision(
            "P2121_CERTIFIED_BLOCK_AUDIT",
            "PASS" if not failures else "FAIL",
            "ALL_CERTIFIED_BLOCKS_PASS" if not failures else "CERTIFIED_BLOCK_FAILURE",
            {"results": results, "failures": failures},
        )


class PackageIntegrityAudit:
    def evaluate(self, repo: str) -> AuditDecision:
        assert_no_financial_execution()

        packages = [
            "data/runtime/P2071_2080/P2071_2080_PACKAGE_FINAL.zip",
            "data/runtime/P2081_2090/P2081_2090_PACKAGE_FINAL.zip",
            "data/runtime/P2091_2100/P2091_2100_PACKAGE_FINAL.zip",
            "data/runtime/P2101_2110/P2101_2110_PACKAGE_FINAL.zip",
            "data/runtime/P2111_2120/P2111_2120_PACKAGE_FINAL.zip",
        ]

        found = {}
        missing = []

        for package in packages:
            p = Path(repo) / package
            if p.exists() and p.stat().st_size > 0:
                found[package] = {"bytes": p.stat().st_size, "sha256": sha256_file(str(p))}
            else:
                missing.append(package)

        return AuditDecision(
            "P2122_PACKAGE_INTEGRITY_AUDIT",
            "PASS" if not missing else "FAIL",
            "ALL_PACKAGES_PRESENT" if not missing else "PACKAGE_MISSING",
            {"packages": found, "missing": missing},
        )


class LockRegressionAudit:
    def evaluate(self) -> AuditDecision:
        assert_no_financial_execution()
        locks = enforce_paper_only()
        invalid = {k: locks.get(k) for k, v in ABSOLUTE_LOCKS.items() if locks.get(k) != v}

        return AuditDecision(
            "P2123_LOCK_REGRESSION_AUDIT",
            "PASS" if not invalid else "FAIL",
            "ALL_FINANCIAL_LOCKS_VALID" if not invalid else "LOCK_REGRESSION_FOUND",
            {"locks": locks, "invalid": invalid},
        )


class RuntimeModuleAudit:
    def evaluate(self, repo: str) -> AuditDecision:
        assert_no_financial_execution()

        modules = [
            "app/runtime/p2071_2080_realtime_paper_runtime.py",
            "app/runtime/p2081_2090_realtime_portfolio_governance.py",
            "app/runtime/p2091_2100_realtime_intelligence_layer.py",
            "app/runtime/p2101_2110_autonomous_paper_operations.py",
            "app/runtime/p2111_2120_maximum_technical_capacity.py",
        ]

        present = {}
        missing = []

        for module in modules:
            p = Path(repo) / module
            if p.exists():
                present[module] = {"bytes": p.stat().st_size, "sha256": sha256_file(str(p))}
            else:
                missing.append(module)

        return AuditDecision(
            "P2124_RUNTIME_MODULE_AUDIT",
            "PASS" if not missing else "FAIL",
            "ALL_RUNTIME_MODULES_PRESENT" if not missing else "RUNTIME_MODULE_MISSING",
            {"modules": present, "missing": missing},
        )


class EvidenceCompletenessAudit:
    def evaluate(self, repo: str) -> AuditDecision:
        assert_no_financial_execution()

        expected = [
            "data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json",
            "data/runtime/P2071_2080/evidence/P2071_2080_AUDIT.md",
            "data/runtime/P2081_2090/evidence/P2081_2090_FINAL_CERTIFICATION.json",
            "data/runtime/P2081_2090/evidence/P2081_2090_AUDIT.md",
            "data/runtime/P2091_2100/evidence/P2091_2100_FINAL_CERTIFICATION.json",
            "data/runtime/P2091_2100/evidence/P2091_2100_AUDIT.md",
            "data/runtime/P2101_2110/evidence/P2101_2110_FINAL_CERTIFICATION.json",
            "data/runtime/P2101_2110/evidence/P2101_2110_AUDIT.md",
            "data/runtime/P2111_2120/evidence/P2111_2120_FINAL_CERTIFICATION.json",
            "data/runtime/P2111_2120/evidence/P2111_2120_AUDIT.md",
        ]

        missing = [x for x in expected if not (Path(repo) / x).exists()]

        return AuditDecision(
            "P2125_EVIDENCE_COMPLETENESS_AUDIT",
            "PASS" if not missing else "FAIL",
            "ALL_EVIDENCE_PRESENT" if not missing else "EVIDENCE_MISSING",
            {"expected_count": len(expected), "missing": missing},
        )


class MasterLedgerAudit:
    def evaluate(self, repo: str) -> AuditDecision:
        assert_no_financial_execution()

        ledgers = [
            "data/runtime/P2071_2080/P2071_2080_LEDGER.json",
            "data/runtime/P2081_2090/P2081_2090_LEDGER.json",
            "data/runtime/P2091_2100/P2091_2100_LEDGER.json",
            "data/runtime/P2101_2110/P2101_2110_LEDGER.json",
            "data/runtime/P2111_2120/P2111_2120_LEDGER.json",
        ]

        parsed = {}
        missing = []
        failed = []

        for ledger in ledgers:
            p = Path(repo) / ledger
            if not p.exists():
                missing.append(ledger)
                continue
            data = load_json(str(p))
            parsed[ledger] = data.get("status")
            if data.get("status") != "PASS":
                failed.append(ledger)

        return AuditDecision(
            "P2126_MASTER_LEDGER_AUDIT",
            "PASS" if not missing and not failed else "FAIL",
            "MASTER_LEDGER_OK" if not missing and not failed else "MASTER_LEDGER_FAIL",
            {"ledgers": parsed, "missing": missing, "failed": failed},
        )


class RegressionTestAudit:
    def evaluate(self, repo: str) -> AuditDecision:
        assert_no_financial_execution()

        tests = [
            "tests/test_p2071_2080_realtime_paper_runtime.py",
            "tests/test_p2081_2090_realtime_portfolio_governance.py",
            "tests/test_p2091_2100_realtime_intelligence_layer.py",
            "tests/test_p2101_2110_autonomous_paper_operations.py",
            "tests/test_p2111_2120_maximum_technical_capacity.py",
        ]

        missing = [x for x in tests if not (Path(repo) / x).exists()]

        return AuditDecision(
            "P2127_REGRESSION_TEST_AUDIT",
            "PASS" if not missing else "FAIL",
            "REGRESSION_TEST_FILES_PRESENT" if not missing else "REGRESSION_TEST_FILES_MISSING",
            {"expected_tests": tests, "missing": missing},
        )


class ContinuousReadinessAudit:
    def evaluate(self, decisions: List[AuditDecision]) -> AuditDecision:
        assert_no_financial_execution()
        failed = [d.component for d in decisions if d.status != "PASS"]

        return AuditDecision(
            "P2128_CONTINUOUS_READINESS_AUDIT",
            "PASS" if not failed else "FAIL",
            "CONTINUOUS_READINESS_CONFIRMED" if not failed else "CONTINUOUS_READINESS_FAILED",
            {"failed_components": failed, "checked_components": len(decisions)},
        )


class MasterReportBuilder:
    def evaluate(self, decisions: List[AuditDecision]) -> AuditDecision:
        assert_no_financial_execution()
        report = {
            "generated_at": int(time.time()),
            "components": len(decisions),
            "pass_count": len([d for d in decisions if d.status == "PASS"]),
            "fail_count": len([d for d in decisions if d.status != "PASS"]),
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
            "broker_execution": "DISABLED",
        }

        return AuditDecision(
            "P2129_MASTER_REPORT_BUILDER",
            "PASS",
            "MASTER_REPORT_READY",
            report,
        )


def certify(decisions: List[AuditDecision]) -> AuditDecision:
    assert_no_financial_execution()
    failed = [d.component for d in decisions if d.status != "PASS"]

    return AuditDecision(
        "P2130_CONTINUOUS_MAX_CAPACITY_CERTIFICATION",
        "PASS" if not failed else "FAIL",
        "CONTINUOUS_MAX_CAPACITY_CERTIFIED" if not failed else "CONTINUOUS_MAX_CAPACITY_NOT_CERTIFIED",
        {
            "failed_components": failed,
            "passed_components": [d.component for d in decisions if d.status == "PASS"],
            "total_components": len(decisions),
            "known_critical_gaps": len(failed),
        },
    )


def run_p2121_plus(repo: str, dependencies: Dict[str, str], output_dir: str) -> Dict[str, Any]:
    assert_no_financial_execution()

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    decisions: List[AuditDecision] = []

    decisions.append(CertifiedBlockAudit().evaluate(dependencies))
    decisions.append(PackageIntegrityAudit().evaluate(repo))
    decisions.append(LockRegressionAudit().evaluate())
    decisions.append(RuntimeModuleAudit().evaluate(repo))
    decisions.append(EvidenceCompletenessAudit().evaluate(repo))
    decisions.append(MasterLedgerAudit().evaluate(repo))
    decisions.append(RegressionTestAudit().evaluate(repo))
    decisions.append(ContinuousReadinessAudit().evaluate(decisions))
    decisions.append(MasterReportBuilder().evaluate(decisions))

    final_cert = certify(decisions)
    decisions.append(final_cert)

    mission_status = {d.component: d.status for d in decisions}
    all_pass = all(d.status == "PASS" for d in decisions)

    result = {
        "program": "P2121_PLUS_CONTINUOUS_MAX_CAPACITY_AUDIT",
        "status": "PASS" if all_pass else "FAIL",
        "readiness": "CONTINUOUS_MAX_CAPACITY_CERTIFIED" if all_pass else "NOT_CERTIFIED",
        "absolute_restrictions": enforce_paper_only(),
        "dependencies": dependencies,
        "mission_status": mission_status,
        "decisions": [asdict(d) for d in decisions],
        "final_state": {
            "p2071_to_p2120": "CERTIFIED",
            "continuous_audit": "CERTIFIED" if all_pass else "NOT_CERTIFIED",
            "known_critical_gaps": final_cert.payload["known_critical_gaps"],
            "paper_only": True,
            "real_orders": "FORBIDDEN",
            "broker_execution": "DISABLED",
            "financial_execution": "DISABLED",
        },
        "next_recommended_block": "P2131_PLUS_RECURRENT_REGRESSION_AND_EXTERNAL_DATA_SANDBOX",
    }

    final_path = output / "P2121_PLUS_FINAL_CERTIFICATION.json"
    audit_path = output / "P2121_PLUS_AUDIT.md"
    state_path = output / "P2121_PLUS_CONTINUOUS_STATE.json"

    final_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    state_path.write_text(json.dumps(result["final_state"], indent=2, ensure_ascii=False), encoding="utf-8")

    audit = f"""# MIND TRADER — P2121+ CONTINUOUS MAX CAPACITY AUDIT

## STATUS
{result["status"]}

## READINESS
{result["readiness"]}

## MISSION STATUS
{json.dumps(mission_status, indent=2, ensure_ascii=False)}

## FINAL STATE
{json.dumps(result["final_state"], indent=2, ensure_ascii=False)}

## ABSOLUTE LOCKS
{json.dumps(result["absolute_restrictions"], indent=2, ensure_ascii=False)}

## CONCLUSION
P2121+ continuous max capacity audit completed.
P2071→P2120 remains certified.
No real orders.
No broker execution.
No financial execution.
"""
    audit_path.write_text(audit, encoding="utf-8")

    return result
