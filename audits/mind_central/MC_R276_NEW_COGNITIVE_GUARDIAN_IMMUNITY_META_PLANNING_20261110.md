# MC R276 — Three new cognition discoveries, 2026-11-10

New historical Drive sources inventoried and preserved in isolated GitHub branch:
1. `app/cognition/guardian_mind.py`, Drive `1I709UmYU7jhKe0IgkVQdJ9tb0TnfUAGd`: explicitly states it **never intervenes, only signals**. Missing reality data defaults to certainty 1.0; protection_score starts 1.0. Therefore cannot serve as authorization enforcement.
2. `app/cognition/meta_planning.py`, Drive `1vCHkFcidyj_IscNg2dY07w7r6fRBe4hB`: FastAPI /plan; ranks modules for growth/stability/efficiency, suggests accelerate/maintain/monitor. Its max/min clamp does not reject NaN. No independent permission checks.
3. `app/cognition/immunity.py`, Drive `1cOWgEU__7TMY5XfAio_1b97LWw501Zq2`: **newly found dependency**. It explicitly does not block; only flags out-of-range and invalid types. `float('nan')` passes both comparisons and is not flagged; `bool` is accepted as numeric. This is a source-derived logic finding, not a behavioral test.

All three source contents are published under `audits/mind_central/r276/originals/`. **No original engine execution or integration in this round.** Required next: offline tests for NaN/bool/missing-state, deny-only enforcement outside GuardianMind/ImmuneSystem, dependency wiring, then certification review. Ledger entry attempted on actual native Google Doc; write failed `403 PERMISSION_DENIED`; this audit is pending ledger entry. Main/production untouched; no real orders; HP19=0/19; R$0.
