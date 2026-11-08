# ET665.R189 — Offline harness hardening (2026-11-08)

Direct source inspection of R187 harness found that the evidence directory was nested under the repository mounted read-only, then remounted read-write inside Docker. This weakens the separation between immutable test sources and writable outputs.

R189 changes the default evidence directory to a sibling of the repository, rejects evidence paths inside the source checkout, rejects reuse of existing evidence directories, applies restrictive permissions, verifies the Git HEAD and creates a deterministic file hash manifest.

Follow-up hardening: canonicalize the evidence parent, reject symlinked evidence targets and dirty tracked source checkouts, and create the evidence directory exclusively with restrictive umask. All five named test files were confirmed present on the R189 branch through authenticated GitHub file reads; this does not establish test execution or compatibility.

These changes are source-level only. No Docker runtime execution, network isolation proof, pytest PASS, branch-protection change, Drive reconciliation or independent certification has occurred. The default evidence directory must be absent before invocation. Runtime evidence and manual security review remain mandatory.

`R189=PATCH_PROPOSED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
