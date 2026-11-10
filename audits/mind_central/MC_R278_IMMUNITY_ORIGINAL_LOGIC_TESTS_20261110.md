# MC R278 — Immunity behavioral reproduction

Drive source: `1cOWgEU__7TMY5XfAio_1b97LWw501Zq2`, recovered in R276 and preserved in isolated GitHub branch `audits/mind_central/r276/originals/immunity.py`.

**6/6 offline unittest PASS** using a **manually transcribed local copy** of the source; binary identity to Drive original not certified. Executed with `python -m unittest -v test_r278`. Findings: NaN score produces no flags; bool score produces no flags; absent score defaults to 0 without alert; strings flagged; out-of-range flagged; +infinity clamped to 1. Tests show current defects, **not** successful safety enforcement.

Local transcribed source SHA256: `7cddd1882901bb67c8454c9aa9c866c80411cadd03bbcd3f54adce9e089b0c58`; test SHA256: `0bcd2bac97b4577316db5736b8b76d7a3499b1fd7dda6a3e08023e86c15f5257`.

Next: test byte-identical original and GuardianMind integration with independent fail-closed guard; R277 guard remains isolated. No merge, production, live orders or certification. Master Ledger append 403. HP19=0/19, R$0.
