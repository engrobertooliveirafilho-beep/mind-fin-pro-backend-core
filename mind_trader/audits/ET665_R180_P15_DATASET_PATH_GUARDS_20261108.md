# ET665.R180 — P15 dataset path containment (2026-11-08)

## Finding
P15.16 and P15.25B consumed dataset names from JSON queue/edge records by joining them directly to the normalized staging directory. The prior implementation had no explicit rejection for absolute paths, parent traversal, NUL-containing names, or symlink escapes. A modified queue/edge record could therefore cause reads outside the intended normalized dataset area.

## Remediation published
- P15.16: added `safe_dataset_path()`; `run()` resolves each queue dataset through the guard before checking/reading it.
- P15.25B: added the same guard; `load_dataset()` resolves every edge dataset through it.
- Guard rejects non-string/blank/NUL names, POSIX and Windows absolute paths, drive-qualified paths, `..` components, root symlinks, component symlinks, resolved escapes, and existing non-file targets.
- No broker, MT5, network, Drive write, production route, or real order was used.

## Git evidence
- Branch: `audit/et665-r180-p15-dataset-path-guards-20261108`
- P15.16 blob: `3fe51f4804f1d5c5303e579539d5127ee761f10e`
- P15.25B blob: `670446d7fe71456e41c96828f3b325f571355e95`
- Regression source blob: `3f7ff22092a94cdbb7260c266069394e838bcde6`
- Regression file: `mind_trader/tests/security_review/test_et665_r180_p15_dataset_path_guards.py`
- 24 parameterized test cases are prepared across valid nested paths, traversal/absolute/malformed names, file symlink escape, and normalized-root symlink escape.

## Verification boundary
The tests were published but NOT EXECUTED. No claim of PASS is made. They must be run in the user's existing offline Docker environment. Symlink cases are written to skip only when Windows/host permissions make symlink creation unavailable; the lexical traversal and absolute-path cases remain mandatory.

## Status
`CODE=PUBLISHED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | SECURITY_APPROVAL=NOT_GRANTED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=UNCHANGED`
