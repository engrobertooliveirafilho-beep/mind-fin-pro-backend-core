# ET665.R250 — Positive fixture correction and evidence boundary

Date: 2026-11-08. Scope: P15.25, draft PR #18.

## Finding
Authenticated source inspection of R249 showed that the positive CSV fixture used literal backslash-n sequences rather than actual CSV row separators. This made the purported positive control unreliable: the CSV parser could read a single header with no data rows, so the expected two closing prices would fail.

## Correction
Updated `test_et665_r247_dataset_containment.py` to use Python newline escapes (`"close\\n101\\n102\\n"` in source), yielding three physical CSV lines at runtime. A follow-up authenticated read confirmed the intended escaped source literal and no embedded source-code newline inside the string.

## Certification
SOURCE_PATCHED / TEST_NOT_EXECUTED. No claim of successful unittest, Docker, CI, independent review, MT5 isolation, R113 integration or R60 reconciliation. Keep PR #18 draft and unmerged; FASE_B=0/16; HP19=0/19; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
