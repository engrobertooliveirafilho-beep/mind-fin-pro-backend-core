# HP19 R255 — adversarial placeholder detection tests (2026-11-10)

Actual local offline execution against `/mnt/data/HP19_R246/hp19_gate.py` and original `agent_sec_sentinel.py`:

- Original source: `placeholder_detected=True` (PASS)
- Change constant latency `1.3` to `1.4`: `placeholder_detected=False` (bypass reproduced)
- Rename dictionary key `input_received` to `payload_received`: `placeholder_detected=False` (bypass reproduced)

Command: `python /mnt/data/HP19_R255_GATE_ADVERSARIAL_TEST.py`. Result: **3/3 PASS** in 0.011s. Tests prove detection gaps, **not** functional agent certification. `validate_registry` remains deny-all (`FUNCTIONAL_EVIDENCE_NOT_PROVIDED`) even if heuristic misses a placeholder. Therefore no operational activation is authorized. Next: replace brittle pattern matching with positive functional evidence requirements and dedicated behavioral tests; do not auto-certify. HP19=0/19, main/production untouched.
