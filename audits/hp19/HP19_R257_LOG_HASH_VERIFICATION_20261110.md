# HP19 R257 — offline integrity checks

Executed locally on 2026-11-10: `cd /mnt/data/HP19_R257 && python -m unittest -v test_evidence_gate`.

**11/11 PASS** (0.012s): self-reported evidence denied; source tamper; incomplete evidence; missing behavior; missing log; forged digest; invalid digest; traversal; absent approval; log tamper; symlink rejection.

Improvement: verify SHA256 against actual log bytes, constrain log filenames and reject symlinks; final outcome remains `EXTERNAL_VERIFICATION_REQUIRED`. This is a **deny-only prototype**, not a trusted reviewer or functional agent certification. The tests use synthetic log content and do not prove behavioral tests were actually run. Local source files: `/mnt/data/HP19_R257/hp19_evidence_gate.py`, `/mnt/data/HP19_R257/test_evidence_gate.py`, `/mnt/data/HP19_R257/results.txt`. No main/production changes. HP19=0/19.
