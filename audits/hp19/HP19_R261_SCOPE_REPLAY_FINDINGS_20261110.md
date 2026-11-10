# HP19 R261 — offline adversarial findings

Executed on 2026-11-10: three dedicated tests PASS in 0.025 seconds. Environment: local R260 combined gate and synthetic test fixtures.

1. Signed manifest containing 19 **noncanonical** `agent_test_*` IDs passes integrity verification.
2. Identical signed manifest is accepted repeatedly; no replay protection or freshness check.
3. Placeholder source `def run(): return None` with correct hash passes file integrity verification.

These are intentional demonstrations of insufficient **positive** verification; R260 continues to return `certified=False` and remains fail-closed. Next required checks: exact canonical 19-ID allowlist, trusted timestamp/challenge and durable replay ledger, real behavioral execution and independent review. No activation, main modification, or production changes. HP19=0/19.
