# ET665 — R58 blocker closeout protocol
Date: 2026-11-08
Baseline: c66fe747919e6504c7e3fb86e4286612b27dc5f0

## Evidence currently reported by the operator
The ET665_FINAL_V2 macro output supplied in the engineering conversation reports:
- R55_SECURITY: PASS (pytest reached 100%).
- R56_INTEGRITY: PASS; 4,361 tracked files hashed with SHA-256.
- R57_PAPER_DEMO_FTMO: PASS (pytest reached 100%).
- Evidence archive: ET665_FINAL_V2_REPORT_20261107_222449.zip
- Archive SHA-256: 708BF9C48E818670EBF0F44B6867398E9DF60B29C92E130A41D0A1AB41D06B03

These are operator-provided execution results. The archive itself has not been independently retrieved or verified in this review.

## R58.1 — OS-level isolation: OPEN
Why open: the reported pytest and hash runs were executed in the Windows host worktree. A Python environment variable, sparse worktree, or subprocess timeout is not an OS security boundary.
Required closure evidence:
1. Run the same approved test selection in an OS-enforced isolated environment (Windows Sandbox, Hyper-V VM, or approved equivalent) with network disabled, source mounted read-only, output mounted separately, and no broker/MT5 credentials or terminals.
2. Capture the isolation configuration, host/guest build, process identity, network state, mounted-folder permissions, command line, exit codes, logs, and SHA-256 manifest.
3. Have the evidence reviewed; do not mark PASS from a configuration file alone.

## R58.2 — Independent security approval: OPEN
Why open: the implementer and the test runner cannot self-issue an independent approval.
Required closure evidence:
1. Submit the technical opinion, complete test logs, R23/R28 reports, mirror diffs, and OS-isolation evidence to a reviewer who did not implement the remediation.
2. Reviewer records identity, scope, commit SHA, findings, exceptions, and explicit APPROVED / REJECTED decision in GitHub review or signed report.
3. No approval is inferred from a draft PR, green tests, or this protocol.

## R58.3 — Full Drive/GitHub authority and mirror reconciliation: OPEN
Why open: the reported R56 step ran git fsck and hashed tracked Python files; it did not prove all-file Drive-to-Git equivalence or semantic mirror equivalence.
Required closure evidence:
1. Freeze the exact Git commit and Drive source snapshot/version.
2. Export Drive file inventory with canonical path, file ID, size, modified time, and SHA-256 where the provider exposes bytes; record explicit exceptions for native Docs/Sheets/Slides and non-exportable objects.
3. Generate full Git tree inventory for every tracked blob, not Python-only, with Git blob OID and SHA-256.
4. Reconcile canonical Drive paths to Git paths using a reviewed mapping; report missing, extra, byte-identical, and divergent objects.
5. Run R23 full-tree inventory and R28 canonical/mirror drift audit on the same full, non-shallow repository commit; review every sensitive divergence and parse failure.
6. Publish manifests and reconciliation report; no source mutation or automatic overwrite.

## Non-negotiable safety state
PHASE_B=OPEN
CERTIFICATION=NOT_GRANTED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN

## Decision
No code defect is established by these three external governance gates alone. Do not change trading engines merely to make a gate green. R58.1 requires an OS-attested execution, R58.2 requires a genuinely independent human decision, and R58.3 requires the actual Drive inventory and complete Git object inventory.