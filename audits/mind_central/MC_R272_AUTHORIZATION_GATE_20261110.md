# R272 — Deny-only cognitive authorization gateway

Isolated R272 wrapper blocks unauthorized payload fields, unknown engine IDs, forbidden operation strings, extra option metadata, nonfinite scores, and invalid options before calling an engine. Depends on R270 safe_cognitive_gateway and R269 finite_scores.

Offline test: `cd /mnt/data/MC_R272 && python -m unittest -v test_secure_gateway` → 15/15 PASS (fake engines). SHA256 gateway: `287c42b18a103c7626596e6da8a13b8305f7e851ab1543602dbca3c428463edc`; test: `02411db07a39fb46bccffca9a8f73b6044219f00c893300d2dd6af9687b77dae`.

Limits: this wrapper is not a sandbox or trusted authorization framework. Original engines not tested through this wrapper; no deployment or certification. Master Ledger still blocked by Google 403; append pending. HP19=0/19, main unchanged, cost R$0.
