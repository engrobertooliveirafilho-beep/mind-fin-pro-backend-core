# MC R277 — CognitiveImmuneSystem behavioral hardening
2026-11-10. Historical original source recovered in R276 from Drive ID 1cOWgEU__7TMY5XfAio_1b97LWw501Zq2.

13/13 offline unittest PASS on a **locally reconstructed copy of original immunity.py logic**, not byte-identical original. 2 tests reproduce NaN and bool bypass, 11 check denial and valid values. Isolated gate rejects invalid, nonfinite, out-of-range, absent, extra and boolean scores before calling the engine. No production integration, no original byte-identical execution, no HP19 certification.

Local SHA256: gate f676472dfafd329297c1ff8826ed3f4fb9ad0f325e5c5f143ccf0704b5c0f78f; test c12894ee724e5e1a058ce4a4701919c313a4b3e289cd1e778a8b9d1807a8136f. Source file in isolated branch r276/originals/immunity.py. Master Ledger native Docs write blocked 403, this is pending append. MAIN unchanged, R$0.
