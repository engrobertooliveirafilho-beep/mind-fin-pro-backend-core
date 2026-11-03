# ET-461 — Ledger reconciliation (2026-11-03)

Source of truth: Google Drive ELDORA_TRADER_MASTER_REMEDIATION_LEDGER — V1, document 1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI. Read 491 paragraphs (~360k characters). Historical statements are NOT current runtime certifications.

## Historically certified (preserve status; do not upgrade)
- ET-001: 105,461 historical references, 46,092 unique SHA256, 35 packages; documented R2/R2-C reconstruction.
- ET-002: R3-K restore and R3-L runtime freeze; no runtime execution in that gate.
- ET-003: import/factory/composition only; zero cycles and zero orders.
- ET-004: S1 preflight 17/17 historical checks.
- ET-005: S19-R1 60 simulated days, 84,000 reused ticks, 24/24 assertions.
- ET-006: S20 84,000 decisions, 16/16 assertions; directional hit-rate is not OOS/FTMO proof.
- ET-008: historical MT5 data integrity and cloud authority bridge.

## Blocking evidence from ledger
- ET-009: S20 decision ledger lacks symbol; deterministic price join unavailable.
- ET-010: replay-to-dispatch symbol propagation gap.
- ET-011: historical duplicate modules and factories require authority disambiguation.
- ET-012: historical SHA256 for app/runtime/mind_trader_institutional_wiring.py = 3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42. Current Git blob SHA c4cb0cb6759c2df6c7c6717d5708372c0b7c26b4 is a different hash algorithm and cannot be compared directly. Recover authoritative bytes and compute current SHA256 before any equivalence claim.
- ET-458: historical P2223 copies byte-identical, SHA256 ca596c57ea125d8cf4bde6e41f7f3045c13935a3d4b0ba079f4f0c2827e9dde4; legacy daily loss not enforced.
- ET-459: 76 candidate inventory rows; source authority, exact checkout tests and integration remain unverified.

## Three GitHub modules reviewed
- app/api/mind_trader_bulk_capability_control.py: Git blob e72f0df00c95a25b42bec20cd4d68c1d8c696fc9; returns stub_active, NOT operational certification.
- app/runtime/mind_trader_bulk_capability_gate.py: blob cc474be1ecba2214f64d65e5cb2a664a003bd4b2; disabled by default; PAPER_ONLY.
- app/runtime/mind_trader_institutional_wiring.py: blob c4cb0cb6759c2df6c7c6717d5708372c0b7c26b4; imports/health/run counters do not prove strategy quality.

## Completion gates
[x] Historical documentary evidence inventoried and classified.
[x] GitHub existence of the three named files verified.
[x] P2223 historical copy integrity reconciled.
[ ] Original Drive bytes recovered for the three named modules.
[ ] SHA256 matched to authoritative Drive versions.
[ ] Exact GitHub checkout Python 3.12 CI with reproducible tests.
[ ] S20/S21 symbol-to-price deterministic replay and OOS validation.
[ ] FTMO daily/total loss, floating PnL, persistent kill and reset semantics certified.
[ ] Runtime integration authorized and regression-tested.

**Decision:** audit-only branch; no source code mutation, no merge, no real orders. PAPER_ONLY; FTMO_READY=FALSE.
