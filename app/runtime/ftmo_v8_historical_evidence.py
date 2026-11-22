"""Read-only check of the historical FTMO V8 regression manifest."""
from dataclasses import dataclass

EXPECTED = {
    'test_certification_gate_v7': 6,
    'test_execution_v4': 8,
    'test_execution_v5': 8,
    'test_execution_v6': 5,
    'test_portfolio_runtime': 10,
}

@dataclass(frozen=True)
class HistoricalRegressionEvidence:
    count: int
    grouped: dict
    historically_reported_pass: bool
    source_code_verified: bool = False
    runtime_e2e_certified: bool = False

def reconcile_v8_regression_log(log):
    if not isinstance(log, str):
        raise ValueError("historical log must be text")
    import re
    counts = {key: 0 for key in EXPECTED}
    names = set()
    for line in log.splitlines():
        match = re.fullmatch(r'(test_\w+) \((test_\w+)\.\w+\) \.\.\. ok', line.strip())
        if not match:
            continue
        name, suite = match.groups()
        if suite not in EXPECTED or (suite, name) in names:
            raise ValueError("unexpected or duplicate historical test")
        names.add((suite, name))
        counts[suite] += 1
    footer = re.search(r'^Ran (\d+) tests in [\d.]+s$', log, re.MULTILINE)
    reported = int(footer.group(1)) if footer else -1
    passed = counts == EXPECTED and reported == sum(EXPECTED.values()) and re.search(r'^OK$',log,re.MULTILINE) is not None
    return HistoricalRegressionEvidence(len(names),counts,passed)
