# MC R281 — GuardianMind prevalidation gate

2026-11-10. Offline Python unittest **14/14 PASS**, verified locally. New deny-only `checked_scan` validates four telemetry groups, required fields, numeric certainty in [0,1], finite score and output score, and rejects invalid flags/unknown fields. Test engine is a **Spy/Fake Guardian**, not the original GuardianMind. Passing this suite does not prove that the original GuardianMind reads the same telemetry that the gate validates; dependency binding remains a blocker.

SHA256 `guardian_gate.py`: `e922af031e90fdb5758d82d81d61c3db94364b044696083e70d0533075507fae`; `test_guardian_gate.py`: `a3c716cf404d1fe2ad76f750e5a715281d759613d69cdc0ae4edc09107d23f26`.

Sources: GuardianMind historical Drive ID `1I709UmYU7jhKe0IgkVQdJ9tb0TnfUAGd`; four-copy reconciliation R279. GuardianMind is advisory only; this isolated gate does not grant execution authority. No original-engine integration, merge, production or real orders. Master Ledger write pending 403. HP19=0/19; cost R$0.
