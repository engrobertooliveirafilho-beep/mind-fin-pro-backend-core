# R817 — Direct helper fail-closed hardening

2026-11-22. R816 branch left two direct-call paths unsafe: `_call_by_signature()` invoked passed functions and `inspect_capability_module()` imported arbitrary module names. R817 updates both helper bodies on a new isolated branch, preserving signatures but blocking active behavior. `capability_recovery_report()` retains the R816 declared-only behavior.

Local Python unittest: 12/12 PASS on a manually reconstructed, semantically equivalent isolated module (not a byte-identical export of the GitHub file). Local SHA-256: `331dbfe5cdbbfb32e7a999d3ce6370ca589d874a95ad6b3649251fa080dcf8a9` for reconstructed source and `6b9cf27934f92e44b026ffd0241eeb8259cca3b1919f259ec1c8bd2430e442bb` for local tests. Repo-native regression test is published but not executed in repository environment. No production integration, no main merge, no E2E.

R809–R816 historical retrieval and tests preserved; no repeat of 19/19 HP19 stub inventory.
`ISOLATED=12/12 PASS | REPO_TESTS=PENDING | MAIN=INTACT | COST=R$0`
