# ET665.R248 — Cross-platform dataset path hardening

Date: 2026-11-08. Scope: draft PR #18, P15.25 research loader.

## Findings and patch
R247 used `Path.is_absolute()`, which follows the runner OS and does not reliably reject Windows drive or UNC paths on POSIX. R248 adds `PureWindowsPath.is_absolute()` and rejects backslash-containing dataset references, alongside R247's resolved-root containment. The dataset field remains a relative POSIX-style path only.

The R247 symlink fixture was also normalized to a real two-line synthetic CSV. Three new negative tests cover Windows drive, UNC and backslash traversal references.

## Evidence boundary
Source patched and tests published only. No runtime execution, Docker isolation, CI PASS or independent review evidenced. This does not certify all dataset loaders or remove time-of-check/time-of-use filesystem race risks. Keep PR draft, no merge, no production, no real orders. FASE_B=0/16 | HP19=0/19 | COST=R$0.
